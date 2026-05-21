import json
import google.generativeai as genai
from typing import List, Dict, Any

# Local High-Quality Curated Catalog of Hotels for Popular Destinations
HOTEL_CATALOG = {
    "goa": [
        {
            "name": "Zostel Goa (Anjuna)",
            "category": "Budget",
            "price_range": "₹600 - ₹1,200 / night",
            "rating": 4.6,
            "description": "Vibrant backpacker-friendly hostel featuring a swimming pool, social common area, and walking distance to Anjuna beach.",
            "features": ["Free WiFi", "Swimming Pool", "Shared Kitchen", "Social Vibe"],
            "best_for": ["Solo", "Friends"]
        },
        {
            "name": "BloomSuites | Calangute",
            "category": "Mid-Range",
            "price_range": "₹3,500 - ₹5,500 / night",
            "rating": 4.3,
            "description": "Modern and bright hotel in North Goa with comfortable rooms, an outdoor pool, and outstanding service.",
            "features": ["Free Breakfast", "Outdoor Pool", "Fitness Center", "Spa"],
            "best_for": ["Family", "Friends", "Romantic"]
        },
        {
            "name": "Taj Exotica Resort & Spa (South Goa)",
            "category": "Luxury",
            "price_range": "₹15,000 - ₹28,000 / night",
            "rating": 4.8,
            "description": "Mediterranean-style luxury resort overlooking the Arabian Sea, featuring lush gardens, a private beach, and world-class fine dining.",
            "features": ["Private Beach", "Golf Course", "Award-winning Spa", "Kids Play Area"],
            "best_for": ["Family", "Romantic"]
        }
    ],
    "jaipur": [
        {
            "name": "Moustache Hostel Jaipur",
            "category": "Budget",
            "price_range": "₹500 - ₹900 / night",
            "rating": 4.5,
            "description": "Beautifully decorated heritage hostel in the heart of Jaipur. Ideal for backpackers who love rooftop views and cultural activities.",
            "features": ["Free WiFi", "Rooftop Restaurant", "AC Dorms", "Social Events"],
            "best_for": ["Solo", "Friends"]
        },
        {
            "name": "Hotel Pearl Palace",
            "category": "Mid-Range",
            "price_range": "₹2,200 - ₹4,000 / night",
            "rating": 4.4,
            "description": "Award-winning boutique hotel famous for its exquisite rooftop restaurant 'Peacock Rooftop' and authentic Rajasthani hospitality.",
            "features": ["Rooftop Cafe", "Artistic Decor", "Room Service", "Airport Shuttle"],
            "best_for": ["Friends", "Romantic", "Family"]
        },
        {
            "name": "Rambagh Palace (Taj)",
            "category": "Luxury",
            "price_range": "₹25,000 - ₹55,000 / night",
            "rating": 4.9,
            "description": "The jewel of Jaipur, a magnificent palace that was the former residence of the Maharaja. Expect royal treatment and rich history.",
            "features": ["Indoor & Outdoor Pools", "Royal Butler Service", "Spa", "Historic Tours"],
            "best_for": ["Romantic", "Family"]
        }
    ],
    "kerala": [
        {
            "name": "Zostel Munnar",
            "category": "Budget",
            "price_range": "₹700 - ₹1,300 / night",
            "rating": 4.6,
            "description": "Charming container hostel nestled in the misty tea gardens of Munnar. Perfect for budget nature explorers.",
            "features": ["Mountain Views", "Common Lounge", "Bonfire Nights", "Free WiFi"],
            "best_for": ["Solo", "Friends"]
        },
        {
            "name": "Lake Canopy (Alleppey)",
            "category": "Mid-Range",
            "price_range": "₹4,500 - ₹7,500 / night",
            "rating": 4.4,
            "description": "Elegant backwater resort on Punnamada Lake, providing luxurious cottages, scenic pool, and houseboat bookings.",
            "features": ["Backwater Views", "Infinity Pool", "Ayurvedic Spa", "Boating Activites"],
            "best_for": ["Family", "Romantic"]
        },
        {
            "name": "Kumarakom Lake Resort",
            "category": "Luxury",
            "price_range": "₹16,000 - ₹32,000 / night",
            "rating": 4.8,
            "description": "Acclaimed luxury resort combining traditional Kerala architecture with modern luxury. Features winding swimming pools and heritage villas.",
            "features": ["Heritage Villas", "Meandering Pool", "Sunset Cruises", "Traditional Dining"],
            "best_for": ["Romantic", "Family"]
        }
    ],
    "mumbai": [
        {
            "name": "Nap on Map Hostel",
            "category": "Budget",
            "price_range": "₹800 - ₹1,400 / night",
            "rating": 4.3,
            "description": "Cozy, hygienic hostel located in a quiet lane in central Mumbai. Great starting point for solo travelers.",
            "features": ["Free Breakfast", "Co-working Space", "Library", "AC Rooms"],
            "best_for": ["Solo", "Friends"]
        },
        {
            "name": "Fariyas Hotel Colaba",
            "category": "Mid-Range",
            "price_range": "₹6,000 - ₹9,500 / night",
            "rating": 4.2,
            "description": "Premium mid-range business hotel located in Colaba, just a short walk away from the Gateway of India.",
            "features": ["Indoor Pool", "Multi-cuisine Restaurant", "Fitness Center", "Bar"],
            "best_for": ["Family", "Friends"]
        },
        {
            "name": "The Taj Mahal Palace",
            "category": "Luxury",
            "price_range": "₹20,000 - ₹45,000 / night",
            "rating": 4.9,
            "description": "Mumbai's most iconic landmark. Indulge in unparalleled historic luxury and magnificent views of the Arabian Sea and the Gateway.",
            "features": ["Sea-view Rooms", "9 Fine Dining Restaurants", "Luxury Spa", "Heritage Walk"],
            "best_for": ["Romantic", "Family"]
        }
    ]
}

# Fallback basic hotels for any unlisted location
GENERIC_HOTELS = [
    {
        "name": "Local Backpacker's Hostel",
        "category": "Budget",
        "price_range": "₹600 - ₹1,200 / night",
        "rating": 4.4,
        "description": "Highly rated, friendly backpacker hostel located centrally with co-working and social facilities.",
        "features": ["Free WiFi", "Lockers", "Common Area", "Social Events"],
        "best_for": ["Solo", "Friends"]
    },
    {
        "name": "Charming Central Inn",
        "category": "Mid-Range",
        "price_range": "₹2,500 - ₹4,500 / night",
        "rating": 4.2,
        "description": "Comfortable boutique hotel with complimentary breakfast, attentive staff, and comfortable family rooms.",
        "features": ["Free Breakfast", "Room Service", "Free Parking", "AC Rooms"],
        "best_for": ["Family", "Friends", "Romantic"]
    },
    {
        "name": "Grand Palace & Spa Resort",
        "category": "Luxury",
        "price_range": "₹10,000 - ₹20,000 / night",
        "rating": 4.7,
        "description": "Breathtaking premium resort offering elegant suites, fine dining, a signature spa, and exceptional service.",
        "features": ["Swimming Pool", "Spa & Wellness", "Fine Dining", "Concierge Service"],
        "best_for": ["Romantic", "Family"]
    }
]

def get_fallback_hotels(destination: str) -> List[Dict[str, Any]]:
    """Generates localized names using generic templates for fallback."""
    dest_clean = destination.capitalize()
    fallback_list = []
    
    for gh in GENERIC_HOTELS:
        item = gh.copy()
        if "Backpacker" in item["name"]:
            item["name"] = f"Zostel {dest_clean} (or equivalent Backpackers Hostel)"
        elif "Charming" in item["name"]:
            item["name"] = f"{dest_clean} Residency Suites"
        else:
            item["name"] = f"The Royal Palms Resort & Spa {dest_clean}"
        fallback_list.append(item)
        
    return fallback_list

def recommend_hotels(destination: str, budget: float, trip_type: str = "Family", api_key: str = None) -> List[Dict[str, Any]]:
    """
    Recommends three hotels (Budget, Mid-Range, Luxury) for the given destination.
    Uses a high-quality local catalog for popular Indian destinations,
    and falls back to Gemini AI for dynamically generated localized recommendations for other destinations.
    """
    dest_lower = destination.lower().strip()
    
    # 1. Attempt to use local catalog first
    for city_key, hotels in HOTEL_CATALOG.items():
        if city_key in dest_lower or dest_lower in city_key:
            # Sort/highlight based on trip type suitability
            sorted_hotels = []
            for hotel in hotels:
                h_copy = hotel.copy()
                # Flag if it perfectly fits the user's travel companions
                h_copy["recommended_for_you"] = trip_type in h_copy["best_for"]
                sorted_hotels.append(h_copy)
            return sorted_hotels

    # 2. Use Gemini AI for dynamic recommendation if API key is present
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are a smart travel hotel consultant. Your goal is to suggest exactly 3 realistic, real-life hotels/accommodations in '{destination}' matching three distinct pricing tiers: Budget, Mid-Range, and Luxury.
        
        Tailor the descriptions and features to suit a '{trip_type}' trip.
        
        Your output MUST be a valid JSON array containing exactly 3 objects. Do not include markdown tags like ```json or ```.
        
        JSON schema expected:
        [
          {{
            "name": "Exact Name of Budget Hotel/Hostel in {destination}",
            "category": "Budget",
            "price_range": "e.g. ₹600 - ₹1,200 / night",
            "rating": 4.5,
            "description": "Engaging 1-2 sentence description explaining why it's great, its location, and the vibe.",
            "features": ["WiFi", "AC", "etc"],
            "best_for": ["Solo", "Friends"]
          }},
          {{
            "name": "Exact Name of a popular Mid-Range Hotel in {destination}",
            "category": "Mid-Range",
            "price_range": "e.g. ₹3,000 - ₹6,000 / night",
            "rating": 4.3,
            "description": "Engaging 1-2 sentence description.",
            "features": ["Breakfast", "Pool", "etc"],
            "best_for": ["Family", "Romantic", "Friends"]
          }},
          {{
            "name": "Exact Name of a luxury Resort/Hotel in {destination}",
            "category": "Luxury",
            "price_range": "e.g. ₹12,000 - ₹25,000 / night",
            "rating": 4.8,
            "description": "Engaging 1-2 sentence description.",
            "features": ["Spa", "Private Beach", "etc"],
            "best_for": ["Romantic", "Family"]
          }}
        ]
        """
        
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            hotels_data = json.loads(response.text)
            
            # Add recommended flag based on trip_type match
            for h in hotels_data:
                h["recommended_for_you"] = trip_type in h.get("best_for", [])
            return hotels_data
            
        except Exception as e:
            print(f"Dynamic Hotel Recommendation Error: {e}. Falling back to static mock.")
            # Fail silently to fallback
            
    # 3. Fallback to customizable mock generator
    hotels = get_fallback_hotels(destination)
    for h in hotels:
        h["recommended_for_you"] = trip_type in h["best_for"]
    return hotels

if __name__ == "__main__":
    print("Testing Hotel Recommender offline...")
    recs = recommend_hotels("Goa", 20000, "Solo")
    for r in recs:
        print(f"Category: {r['category']} - Name: {r['name']} - Fits Solo?: {r['recommended_for_you']}")
