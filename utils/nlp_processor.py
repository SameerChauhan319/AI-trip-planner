import re
import spacy
from typing import Dict, Any

# Global NLP engine placeholder
nlp = None

def init_spacy():
    """Initializes spaCy, downloading the model if it's missing."""
    global nlp
    if nlp is not None:
        return nlp
    
    try:
        # Try to load existing model
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # If not present, attempt to download it
        import subprocess
        import sys
        try:
            print("Downloading spaCy en_core_web_sm model...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Failed to download spaCy model: {e}. Falling back to Regex NLP.")
            nlp = None
    return nlp

def extract_trip_details(text: str) -> Dict[str, Any]:
    """
    Extracts travel details (destination, budget, days, preferences) from a natural language string.
    Uses spaCy for named entity recognition (NER) and regular expressions for quantitative values.
    
    Args:
        text (str): The natural language query from the user.
        
    Returns:
        dict: A dictionary containing 'destination', 'budget', 'days', and 'preferences'.
    """
    # Clean the input text
    text_clean = text.strip()
    
    # Initialize extraction results with defaults
    details = {
        "destination": "",
        "budget": 15000.0,  # Default budget in INR
        "days": 3,          # Default number of days
        "preferences": []
    }
    
    if not text_clean:
        return details

    # 1. EXTRACT DAYS (Duration)
    # Match patterns like: "4-day", "4 days", "for 4 days", "4 day trip", "3 nights 4 days"
    days_match = re.search(r'(\d+)\s*(?:-|to)?\s*(?:day|night|d\b)', text_clean, re.IGNORECASE)
    if days_match:
        details["days"] = int(days_match.group(1))
    else:
        # Try searching for single numbers that might represent days if adjacent to "trip" or "vacation"
        alt_days_match = re.search(r'(?:trip|stay|visit|vacation)\s*(?:of|for)?\s*(\d+)\s*(?:days)?', text_clean, re.IGNORECASE)
        if alt_days_match:
            details["days"] = int(alt_days_match.group(1))
            
    # Cap days between 1 and 30 for safety and reasonable API calls
    details["days"] = max(1, min(details["days"], 30))

    # 2. EXTRACT BUDGET
    # Match patterns like: "20000", "20,000", "20k", "20 thousand", "20,000 INR", "₹20,000", "Rs 20000"
    # Look for currency symbols or words like "under", "budget of", "around", "limit"
    # Matches currency patterns: ₹/Rs/INR followed by numbers or numbers followed by k/thousand/lakh
    budget_patterns = [
        r'(?:under|below|budget(?:\s+of)?|max(?:imum)?|around|₹|Rs\.?|INR)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|thousand|lakh|lakhs)?',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|thousand|lakh|lakhs)?\s*(?:budget|₹|Rs\.?|INR|rupees)'
    ]
    
    budget_found = False
    for pattern in budget_patterns:
        match = re.search(pattern, text_clean, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace(",", "")
            try:
                val = float(val_str)
                multiplier = match.group(2)
                if multiplier:
                    multiplier = multiplier.lower()
                    if 'k' in multiplier:
                        val *= 1000
                    elif 'thousand' in multiplier:
                        val *= 1000
                    elif 'lakh' in multiplier:
                        val *= 100000
                details["budget"] = val
                budget_found = True
                break
            except ValueError:
                continue
                
    if not budget_found:
        # General numeric extraction for budget if a large number is found (e.g. > 1000)
        numbers = re.findall(r'\b\d+(?:,\d{3})*\b', text_clean)
        for num in numbers:
            val = float(num.replace(",", ""))
            # Assume a number above 500 represents budget rather than days
            if val >= 1000:
                details["budget"] = val
                break

    # 3. EXTRACT DESTINATION
    # Try spaCy NER first if initialized
    spacy_nlp = init_spacy()
    destination_extracted = False
    
    if spacy_nlp:
        doc = spacy_nlp(text_clean)
        # Look for GPE (Geopolitical Entity) or LOC (Location)
        gpe_entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        if gpe_entities:
            # Clean entity name (remove punctuation/determiners)
            dest = gpe_entities[0].strip()
            # Basic validation to ensure it's not a generic word
            if dest.lower() not in ["india", "usa", "europe", "world", "trip", "travel"]:
                details["destination"] = dest
                destination_extracted = True

    # Fallback/Regex-based Destination Extraction if spaCy fails or is unavailable
    if not destination_extracted:
        # Look for common destination pattern triggers: "to X", "visit X", "trip to X", "explore X", "in X"
        dest_match = re.search(r'(?:to|visit|explore|in|go\s+to|planning\s+a\s+trip\s+to)\s+([A-Z][a-zA-Z\s]+?)(?:\s+(?:under|budget|for|with|and|from|on)\b|$)', text_clean)
        if dest_match:
            details["destination"] = dest_match.group(1).strip()
        else:
            # Tokenize and look for capitalized words that aren't starting words unless they are nouns
            words = text_clean.split()
            potential_destinations = []
            for i, word in enumerate(words):
                # Clean word
                word_clean = re.sub(r'[^\w\s]', '', word)
                if not word_clean:
                    continue
                # If word is capitalized and not the first word (or is first but we have no other options)
                if word_clean[0].isupper() and word_clean.lower() not in ["plan", "trip", "i", "we", "my", "our", "a", "the", "under", "budget", "for", "with", "days", "day", "in"]:
                    potential_destinations.append(word_clean)
            if potential_destinations:
                details["destination"] = " ".join(potential_destinations[:2]) # Grab first 1-2 capitalized words
            else:
                # Absolute fallback: search for words in the sentence
                details["destination"] = "Goa" # A reasonable default to guide the user

    # 4. EXTRACT INTERESTS/PREFERENCES
    # Common travel preferences keywords
    pref_keywords = [
        "beach", "beaches", "nightlife", "party", "clubbing", "nature", "trek", "trekking", 
        "historical", "history", "heritage", "temple", "temples", "spiritual", "adventure", 
        "relax", "relaxation", "luxury", "budget", "food", "foodie", "culinary", "shopping", 
        "wildlife", "safari", "scenic", "mountains", "hills", "museum", "art", "family", 
        "romantic", "honeymoon", "solo", "friends", "kid-friendly", "kids", "photography"
    ]
    
    found_prefs = []
    text_lower = text_clean.lower()
    for pref in pref_keywords:
        if re.search(r'\b' + re.escape(pref) + r'\b', text_lower):
            # Normalize words (e.g. beaches -> beach, temples -> temple)
            norm_pref = pref
            if pref == "beaches": norm_pref = "beach"
            if pref == "temples": norm_pref = "temple"
            if pref == "hills": norm_pref = "mountains"
            if pref not in found_prefs:
                found_prefs.append(norm_pref)
                
    # Also extract any words after "with", "interested in", "preferring", "having"
    extra_prefs_match = re.search(r'(?:with|interested\s+in|preferring|having|focused\s+on)\s+([a-zA-Z\s,]+)(?:\s+(?:under|budget|for|in)\b|$)', text_clean, re.IGNORECASE)
    if extra_prefs_match:
        phrases = [p.strip().lower() for p in re.split(r',|and', extra_prefs_match.group(1))]
        for phrase in phrases:
            if phrase and phrase not in found_prefs and len(phrase) < 25 and phrase not in ["days", "day", "budget", "rupees", "inr"]:
                found_prefs.append(phrase)
                
    details["preferences"] = found_prefs if found_prefs else ["sightseeing", "local food", "culture"]

    # Final cleanup of destination
    details["destination"] = re.sub(r'\b(trip|vacation|tour|travel|days|day|budget)\b', '', details["destination"], flags=re.IGNORECASE).strip()
    if not details["destination"]:
        details["destination"] = "Goa" # default fallback
        
    return details

if __name__ == "__main__":
    # Test cases
    test_queries = [
        "Plan a 4-day Goa trip under ₹20,000 with beaches and nightlife",
        "Generate a detailed 3-day itinerary for Jaipur under ₹15,000 including historical places and shopping",
        "I want to visit Kerala for 5 days with a budget of 35k, looking for scenic beauty and relaxation",
        "Trip to Mumbai for 2 days under 8000"
    ]
    
    print("Testing NLP Extraction...")
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        res = extract_trip_details(q)
        print(f"Extracted: {res}")
