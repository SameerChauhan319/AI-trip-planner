import json
import google.generativeai as genai
from typing import Dict, Any, List


def get_demo_itinerary(destination: str, days: int, budget: float, preferences: List[str]) -> Dict[str, Any]:
    """Generates a high-quality mock itinerary with real, destination-specific landmarks."""
    prefs_str = ", ".join(preferences)

    # Budget breakdown
    total = budget
    hotel_cost  = int(total * (0.35 if budget > 30000 else 0.30))
    food_cost   = int(total * 0.25)
    trans_cost  = int(total * 0.20)
    attr_cost   = int(total * 0.15)
    misc_cost   = int(total - (hotel_cost + food_cost + trans_cost + attr_cost))

    dest_lower = destination.lower().strip()

    # ── Real destination database ─────────────────────────────────────────────
    DEST_DATA = {
        "goa": {
            "lat": 15.2993, "lon": 74.1240,
            "activities": [
                {"activity": "Calangute Beach Morning Walk",
                 "description": "Stroll along Calangute — Goa's largest beach. Enjoy golden sands, fresh coconut water from beach shacks, and the vibrant sunrise atmosphere.",
                 "location": "Calangute Beach, North Goa", "cost": int(total*0.01), "rating": 4.5, "reviews_count": 892},
                {"activity": "Basilica of Bom Jesus Visit",
                 "description": "Explore this UNESCO World Heritage Site, home to the mortal remains of St. Francis Xavier. The 16th-century baroque architecture is breathtaking.",
                 "location": "Basilica of Bom Jesus, Old Goa", "cost": 0, "rating": 4.8, "reviews_count": 1150},
                {"activity": "Dudhsagar Waterfalls Trek",
                 "description": "Hike through Bhagwan Mahavir Wildlife Sanctuary to reach one of India's tallest waterfalls — the milk-white 310m Dudhsagar Falls.",
                 "location": "Dudhsagar Falls, Sanguem Taluka, Goa", "cost": int(total*0.05), "rating": 4.7, "reviews_count": 745},
                {"activity": "Anjuna Flea Market Shopping",
                 "description": "Browse hundreds of stalls selling Goan spices, handmade jewellery, boho clothing, and local art at this iconic Wednesday market.",
                 "location": "Anjuna Flea Market, Anjuna Beach, North Goa", "cost": int(total*0.04), "rating": 4.3, "reviews_count": 610},
                {"activity": "Fort Aguada Sunset Visit",
                 "description": "Climb the 17th-century Portuguese fort for panoramic views of the Arabian Sea at golden hour. The lighthouse and battlements are iconic.",
                 "location": "Fort Aguada, Sinquerim, North Goa", "cost": int(total*0.01), "rating": 4.6, "reviews_count": 820},
                {"activity": "Sahakari Spice Farm Tour & Lunch",
                 "description": "Tour a working spice plantation, see live cardamom, pepper and vanilla trees, and enjoy a traditional Goan thali lunch in the farm.",
                 "location": "Sahakari Spice Farm, Ponda, Goa", "cost": int(total*0.04), "rating": 4.5, "reviews_count": 540},
            ],
            "food": [
                {"name": "Fisherman's Wharf", "type": "Goan Seafood & Fish Curry Rice", "cost_rating": "Medium"},
                {"name": "Britto's Beach Shack", "type": "Beachside Goan Cuisine & Drinks", "cost_rating": "Medium"},
                {"name": "Thalassa Greek Taverna", "type": "Mediterranean & Seafood Fusion", "cost_rating": "Luxury"},
            ],
            "transport": {
                "local_commute": "Rent a scooter (₹300–400/day) from Calangute or Baga. Auto-rickshaws available for short distances.",
                "interstate_commute": "Fly into Dabolim Airport (GOI) or take the Konkan Kanya Express from Mumbai (8–9 hrs)."
            },
            "tips": [
                "Visit beaches early morning (6–8 AM) to avoid crowds and enjoy the best light.",
                "Carry cash — many beach shacks and local vendors don't accept UPI or cards.",
                "Book Dudhsagar jeep safari in advance during peak season (Oct–Feb)."
            ]
        },
        "jaipur": {
            "lat": 26.9124, "lon": 75.7873,
            "activities": [
                {"activity": "Amber Fort Morning Exploration",
                 "description": "Explore the magnificent 16th-century Amber Fort — a UNESCO site perched on a hill with stunning mirror palace (Sheesh Mahal) and intricate Rajput architecture.",
                 "location": "Amber Fort (Amer Fort), Amer, Jaipur", "cost": int(total*0.03), "rating": 4.8, "reviews_count": 1180},
                {"activity": "Hawa Mahal Photography Stop",
                 "description": "Photograph the iconic 'Palace of Winds' — its 953 small jharokha windows were designed for royal women to watch street festivals unseen.",
                 "location": "Hawa Mahal, Badi Choupad, Pink City, Jaipur", "cost": int(total*0.01), "rating": 4.6, "reviews_count": 980},
                {"activity": "City Palace Museum Tour",
                 "description": "Wander through the royal residence of Jaipur's Maharaja. See priceless royal artefacts, costumes, and weapons in the museum complex.",
                 "location": "City Palace, Jaleb Chowk, Pink City, Jaipur", "cost": int(total*0.03), "rating": 4.7, "reviews_count": 870},
                {"activity": "Jantar Mantar UNESCO Observatory",
                 "description": "Walk through the world's largest stone sundial and UNESCO-listed astronomical instruments built by Maharaja Sawai Jai Singh II in 1734.",
                 "location": "Jantar Mantar, Gangori Bazaar, Pink City, Jaipur", "cost": int(total*0.01), "rating": 4.5, "reviews_count": 650},
                {"activity": "Johari Bazaar Gem & Jewellery Shopping",
                 "description": "Explore Jaipur's famous jewellery market — known as the gem-cutting capital of the world. Bargain for precious stones, kundan, and meenakari jewellery.",
                 "location": "Johari Bazaar, Pink City, Jaipur", "cost": int(total*0.06), "rating": 4.4, "reviews_count": 720},
                {"activity": "Nahargarh Fort Sunset View",
                 "description": "Drive up the Aravalli hills to Nahargarh Fort for a sweeping panoramic view of Jaipur's Pink City skyline glowing at dusk.",
                 "location": "Nahargarh Fort, Krishna Nagar, Jaipur", "cost": int(total*0.02), "rating": 4.6, "reviews_count": 790},
            ],
            "food": [
                {"name": "Laxmi Misthan Bhandar (LMB)", "type": "Rajasthani Thali & Traditional Sweets", "cost_rating": "Budget"},
                {"name": "Suvarna Mahal, Rambagh Palace", "type": "Royal Rajput Fine Dining", "cost_rating": "Luxury"},
                {"name": "Peacock Rooftop Restaurant", "type": "North Indian & Continental with City Views", "cost_rating": "Medium"},
            ],
            "transport": {
                "local_commute": "Use metered auto-rickshaws or Ola/Uber. Hire a local guide (₹500–800/day) for old city bazaars.",
                "interstate_commute": "Jaipur is 5 hrs from Delhi by road or Shatabdi Express. Jaipur International Airport has direct flights."
            },
            "tips": [
                "Start with Amber Fort before 9 AM to beat the tourist rush and heat.",
                "The Pink City bazaars are best explored on foot — wear comfortable shoes.",
                "Always bargain for gems and textiles — starting price is typically 3× the fair value."
            ]
        },
        "mumbai": {
            "lat": 18.9388, "lon": 72.8354,
            "activities": [
                {"activity": "Gateway of India & Colaba Walk",
                 "description": "Start at the iconic 1924 colonial arch overlooking the Arabian Sea, then stroll Colaba Causeway for street shopping and street food.",
                 "location": "Gateway of India, Apollo Bunder, Colaba, Mumbai", "cost": 0, "rating": 4.7, "reviews_count": 1200},
                {"activity": "Elephanta Caves Ferry Excursion",
                 "description": "Take a 1-hr ferry from Gateway of India to UNESCO-listed Elephanta Island — home to magnificent 7th-century rock-cut Shiva temple caves.",
                 "location": "Elephanta Caves, Gharapuri Island, Mumbai Harbour", "cost": int(total*0.03), "rating": 4.5, "reviews_count": 760},
                {"activity": "Marine Drive Sunset Promenade",
                 "description": "Walk the 3.6km Queen's Necklace promenade at sunset — Art Deco buildings on one side, glittering Arabian Sea on the other. A Mumbai classic.",
                 "location": "Marine Drive (Netaji Subhash Chandra Bose Road), South Mumbai", "cost": 0, "rating": 4.8, "reviews_count": 1050},
                {"activity": "Dharavi Cultural Walking Tour",
                 "description": "Join a guided cultural tour of Asia's most densely populated urban community — visit working factories, pottery workshops, and recycling units.",
                 "location": "Dharavi, Sion, Mumbai", "cost": int(total*0.02), "rating": 4.6, "reviews_count": 480},
                {"activity": "CST Victoria Terminus Heritage Visit",
                 "description": "Marvel at this stunning UNESCO-listed Victorian Gothic railway station built in 1887. Its gargoyles, turrets and stained glass make it one of Asia's finest buildings.",
                 "location": "Chhatrapati Shivaji Maharaj Terminus (CST), Bori Bunder, Mumbai", "cost": 0, "rating": 4.7, "reviews_count": 890},
                {"activity": "Bandra Sea Link & Cafe Hopping",
                 "description": "Cross the iconic cable-stayed bridge then explore Bandra's bohemian lane cafes, street art, and the vibrant Hill Road market scene.",
                 "location": "Bandra-Worli Sea Link & Bandra West, Mumbai", "cost": int(total*0.03), "rating": 4.5, "reviews_count": 620},
            ],
            "food": [
                {"name": "Britannia & Co., Ballard Estate", "type": "Iconic Irani Cafe — Berry Pulao & Sali Boti", "cost_rating": "Budget"},
                {"name": "Leopold Cafe, Colaba", "type": "Continental & Indian — Colaba Institution", "cost_rating": "Medium"},
                {"name": "Trishna, Kala Ghoda", "type": "Legendary Seafood & Coastal Cuisine", "cost_rating": "Luxury"},
            ],
            "transport": {
                "local_commute": "Use Mumbai Local Trains (cheapest & fastest). Ola/Uber for nights. Auto-rickshaws only in suburbs.",
                "interstate_commute": "Chhatrapati Shivaji Maharaj International Airport handles all major airlines. Central & Western Railway connect to all metros."
            },
            "tips": [
                "Get an MMRC Metro/local train day pass to save on travel costs.",
                "Avoid 8–10 AM and 5–8 PM rush hours in local trains.",
                "Monsoon (June–Aug) brings heavy rains — always carry a compact umbrella."
            ]
        },
        "delhi": {
            "lat": 28.6448, "lon": 77.2167,
            "activities": [
                {"activity": "Red Fort (Lal Qila) Morning Visit",
                 "description": "Explore Shah Jahan's red sandstone masterpiece — a UNESCO World Heritage Site. Walk through the Diwan-i-Aam, Diwan-i-Khas and royal gardens.",
                 "location": "Red Fort (Lal Qila), Chandni Chowk, Old Delhi", "cost": int(total*0.01), "rating": 4.6, "reviews_count": 1080},
                {"activity": "Qutub Minar Complex",
                 "description": "Visit the world's tallest brick minaret (72.5m), built in 1193 AD. The surrounding ruins of the Quwwat-ul-Islam Mosque are equally stunning.",
                 "location": "Qutub Minar, Mehrauli, South Delhi", "cost": int(total*0.01), "rating": 4.7, "reviews_count": 970},
                {"activity": "Humayun's Tomb Garden Walk",
                 "description": "Stroll through the Persian-style char bagh gardens of this 16th-century Mughal tomb — the architectural precursor to the Taj Mahal. UNESCO site.",
                 "location": "Humayun's Tomb, Nizamuddin East, New Delhi", "cost": int(total*0.02), "rating": 4.7, "reviews_count": 830},
                {"activity": "Chandni Chowk Street Food Tour",
                 "description": "Dive into Old Delhi's legendary food lane — taste parathe at Paranthe Wali Gali, jalebis at Ghantewala, and kulfi from Kuremal's.",
                 "location": "Chandni Chowk & Paranthe Wali Gali, Old Delhi", "cost": int(total*0.03), "rating": 4.8, "reviews_count": 920},
                {"activity": "India Gate & Kartavya Path",
                 "description": "Walk along the 3km ceremonial boulevard to India Gate — the war memorial honouring 80,000 soldiers. Beautiful at golden hour.",
                 "location": "India Gate, Kartavya Path (Rajpath), New Delhi", "cost": 0, "rating": 4.7, "reviews_count": 1100},
                {"activity": "Lodhi Garden Evening Walk",
                 "description": "Explore Delhi's most beautiful urban park — 90 acres of manicured gardens dotted with 15th-century Sayyid and Lodi dynasty tombs.",
                 "location": "Lodhi Garden, Lodhi Road, New Delhi", "cost": 0, "rating": 4.6, "reviews_count": 680},
            ],
            "food": [
                {"name": "Karim's, Old Delhi", "type": "Mughlai Cuisine — Legendary since 1913", "cost_rating": "Budget"},
                {"name": "Indian Accent, The Lodhi", "type": "Modern Indian Fine Dining", "cost_rating": "Luxury"},
                {"name": "Saravana Bhavan, Connaught Place", "type": "South Indian Tiffin & Thali", "cost_rating": "Budget"},
            ],
            "transport": {
                "local_commute": "Delhi Metro is the best way to travel — connects to all major sights. Use Ola/Uber for early morning or late-night trips.",
                "interstate_commute": "Indira Gandhi International Airport (DEL) is one of Asia's busiest hubs. New Delhi Railway Station connects to the entire country."
            },
            "tips": [
                "Buy a Metro tourist day card (₹200) for unlimited rides on all lines.",
                "Old Delhi is best explored by cycle-rickshaw — negotiate price before boarding.",
                "Visit monuments during golden hour (7–8 AM or 5–6 PM) for stunning photography."
            ]
        },
        "agra": {
            "lat": 27.1767, "lon": 78.0081,
            "activities": [
                {"activity": "Taj Mahal Sunrise Visit",
                 "description": "Witness the world's greatest monument to love glow pink and gold at sunrise — the most magical time to see Emperor Shah Jahan's white marble masterpiece.",
                 "location": "Taj Mahal, Taj Ganj, Agra, Uttar Pradesh", "cost": int(total*0.05), "rating": 4.9, "reviews_count": 1200},
                {"activity": "Agra Fort (Red Fort) Tour",
                 "description": "Explore the massive Mughal fort complex — Shah Jahan spent his final years imprisoned here with a distant view of the Taj Mahal.",
                 "location": "Agra Fort, Rakabganj, Agra", "cost": int(total*0.03), "rating": 4.7, "reviews_count": 870},
                {"activity": "Mehtab Bagh Sunset Garden",
                 "description": "Visit the moonlit garden directly across the Yamuna for the best free sunset view of the Taj Mahal reflecting on the river.",
                 "location": "Mehtab Bagh, Dharmapuri Forest Colony, Agra", "cost": int(total*0.01), "rating": 4.6, "reviews_count": 520},
                {"activity": "Kinari Bazaar & Petha Shopping",
                 "description": "Browse the narrow lanes of Kinari Bazaar for Agra's famous petha sweets, leather goods, marble inlay souvenirs, and Mughal-era crafts.",
                 "location": "Kinari Bazaar, Loha Mandi, Agra", "cost": int(total*0.03), "rating": 4.3, "reviews_count": 410},
            ],
            "food": [
                {"name": "Pinch of Spice", "type": "North Indian & Mughlai Cuisine", "cost_rating": "Medium"},
                {"name": "Dalmoth & Petha at Panchhi Petha", "type": "Agra's Iconic Street Sweets — since 1956", "cost_rating": "Budget"},
            ],
            "transport": {
                "local_commute": "Pre-paid auto-rickshaws from Agra Cantt station. Electric e-rickshaws near Taj Mahal (no petrol vehicles within 500m).",
                "interstate_commute": "Agra Cantt is served by Shatabdi from Delhi (2 hrs). Yamuna Expressway makes it 3.5 hrs by road."
            },
            "tips": [
                "Book Taj Mahal tickets online in advance — entry queues can be 1–2 hours long.",
                "Go for sunrise on weekdays to avoid massive weekend crowds.",
                "Buy authentic Agra petha from Panchhi Petha Store — the city's most iconic sweet."
            ]
        },
        "kerala": {
            "lat": 9.4981, "lon": 76.3388,
            "activities": [
                {"activity": "Alleppey Backwater Houseboat Cruise",
                 "description": "Drift through Kerala's legendary backwater canals on a traditional kettuvallam rice boat, watching coconut palms and village life glide by.",
                 "location": "Alleppey (Alappuzha) Backwaters, Alleppey", "cost": int(total*0.15), "rating": 4.8, "reviews_count": 940},
                {"activity": "Kolukkumalai Tea Estate Trek",
                 "description": "Walk through endless emerald-green tea plantations at 1,600m altitude, visit the Tea Museum, and learn about Munnar's colonial tea heritage.",
                 "location": "Kolukkumalai Tea Estate, Munnar, Kerala", "cost": int(total*0.03), "rating": 4.7, "reviews_count": 720},
                {"activity": "Periyar Tiger Reserve Boat Safari",
                 "description": "Take a guided boat safari across Periyar Lake inside Thekkady wildlife sanctuary — spot elephants, bison, and rare birds along the forested shores.",
                 "location": "Periyar Tiger Reserve, Thekkady, Kerala", "cost": int(total*0.04), "rating": 4.6, "reviews_count": 650},
                {"activity": "Kovalam Beach & Lighthouse",
                 "description": "Relax on Kerala's most famous crescent-shaped beach. Climb the Kovalam lighthouse for a panoramic view of the coast and Arabian Sea.",
                 "location": "Kovalam Beach & Lighthouse, Thiruvananthapuram, Kerala", "cost": int(total*0.01), "rating": 4.5, "reviews_count": 590},
                {"activity": "Kathakali Dance Performance",
                 "description": "Watch an elaborate Kerala classical dance performance with vivid costumes and expressive storytelling based on Hindu epics.",
                 "location": "Kerala Kathakali Centre, Peter Celli Street, Fort Kochi", "cost": int(total*0.03), "rating": 4.7, "reviews_count": 480},
                {"activity": "Fort Kochi & Chinese Fishing Nets",
                 "description": "Explore Fort Kochi's colonial quarter — see the iconic Chinese fishing nets at sunset, walk the waterfront, and visit St. Francis Church.",
                 "location": "Fort Kochi Beach & Chinese Fishing Nets, Kochi", "cost": 0, "rating": 4.6, "reviews_count": 860},
            ],
            "food": [
                {"name": "Dal Roti, Kochi", "type": "Kerala Fish Curry & Appam — Authentic Home Style", "cost_rating": "Budget"},
                {"name": "Fusion Bay, Fort Kochi", "type": "Kerala-Continental Fusion Cuisine", "cost_rating": "Medium"},
                {"name": "Malabar Junction", "type": "Traditional Malabar Seafood & Nadan Curries", "cost_rating": "Luxury"},
            ],
            "transport": {
                "local_commute": "KSRTC buses connect major towns. Rent a car with driver (₹2,000–3,000/day) for flexibility. Autos in cities.",
                "interstate_commute": "Fly to Kochi (COK) or Trivandrum (TRV). Kerala Express and Jan Shatabdi from Chennai/Bangalore."
            },
            "tips": [
                "Book houseboats at least 2 weeks early during Oct–Feb peak season.",
                "Ayurvedic massage centres offer authentic treatments — go for a 2-hr Abhyanga package.",
                "Monsoon (June–Sept) makes waterfalls spectacular but some roads are slippery."
            ]
        },
        "manali": {
            "lat": 32.2396, "lon": 77.1887,
            "activities": [
                {"activity": "Rohtang Pass Snow Adventure",
                 "description": "Drive up to the 3,978m Rohtang Pass for snow activities, breathtaking Himalayan panoramas, and the surreal gateway to the Lahaul Valley.",
                 "location": "Rohtang Pass, Kullu District, Himachal Pradesh", "cost": int(total*0.06), "rating": 4.7, "reviews_count": 890},
                {"activity": "Solang Valley Paragliding & Zorbing",
                 "description": "Try tandem paragliding over the gorgeous Solang Valley, or roll downhill in a transparent zorb ball for an adrenaline rush.",
                 "location": "Solang Valley, 14km North of Manali", "cost": int(total*0.05), "rating": 4.6, "reviews_count": 730},
                {"activity": "Hadimba Devi Temple Visit",
                 "description": "Visit the 1553 AD wooden pagoda temple nestled in a dense cedar forest — dedicated to Hadimba, wife of Bhima from Mahabharata.",
                 "location": "Hadimba Devi Temple, Dhungri Forest, Manali", "cost": 0, "rating": 4.5, "reviews_count": 810},
                {"activity": "Old Manali Village & Vashisht Hot Springs",
                 "description": "Stroll the bohemian cafes and shops of Old Manali, then soak in the natural sulphur hot springs at Vashisht village for muscle relief after trekking.",
                 "location": "Old Manali Village & Vashisht Hot Springs, Manali", "cost": int(total*0.02), "rating": 4.4, "reviews_count": 560},
            ],
            "food": [
                {"name": "Johnson's Cafe, Circuit House Road", "type": "Continental & Himachali Trout Dishes", "cost_rating": "Medium"},
                {"name": "Drifter's Inn & Cafe, Old Manali", "type": "Israeli Breakfast & Backpacker Cafe", "cost_rating": "Budget"},
                {"name": "Casa Bella Vista, Manali", "type": "Italian & Wood-fired Pizza with Mountain Views", "cost_rating": "Medium"},
            ],
            "transport": {
                "local_commute": "Hire a local cab (Tempo Traveller) for Rohtang/Solang — ₹2,500–4,000/day. Rohtang permits must be booked online.",
                "interstate_commute": "Volvo bus from Delhi (14 hrs, ₹800–1,500). Bhuntar Airport is 50km away with flights from Delhi."
            },
            "tips": [
                "Carry warm layers — temperatures drop below 0°C at night even in summer.",
                "Book Rohtang Pass permits online (NGT quota, limited vehicles per day).",
                "Avoid Manali in July–Aug monsoon — landslides can block the Manali-Leh Highway."
            ]
        },
        "thailand": {
            "lat": 13.7563, "lon": 100.5018,
            "activities": [
                {"activity": "Grand Palace & Wat Phra Kaew Visit",
                 "description": "Visit Thailand's most dazzling royal complex — the gilded Grand Palace and the sacred Emerald Buddha temple. Arrive early to beat the crowds.",
                 "location": "The Grand Palace, Na Phra Lan Road, Bangkok", "cost": int(total*0.03), "rating": 4.8, "reviews_count": 1180},
                {"activity": "Chao Phraya River Long-tail Boat Ride",
                 "description": "Hop on a local long-tail boat along the Chao Phraya, visiting Wat Arun (Temple of Dawn) and the khlongs (canals) of Thonburi.",
                 "location": "Chao Phraya River & Wat Arun, Thonburi, Bangkok", "cost": int(total*0.02), "rating": 4.7, "reviews_count": 870},
                {"activity": "Phi Phi Islands Snorkelling Day Trip",
                 "description": "Take a speedboat to Maya Bay (from 'The Beach') and snorkel the crystal-clear Andaman waters around the iconic Phi Phi islands.",
                 "location": "Koh Phi Phi Don & Maya Bay, Krabi Province, Thailand", "cost": int(total*0.07), "rating": 4.8, "reviews_count": 950},
                {"activity": "Patong Beach & Bangla Road Night",
                 "description": "Relax on Phuket's most famous beach by day. At night, explore the neon-lit Bangla Road for street food, live music and entertainment.",
                 "location": "Patong Beach & Bangla Road, Patong, Phuket", "cost": int(total*0.04), "rating": 4.4, "reviews_count": 780},
                {"activity": "Doi Inthanon National Park Trek",
                 "description": "Trek to Thailand's highest peak (2,565m) with twin royal chedis, dramatic waterfalls, and misty hill-tribe villages — a perfect Chiang Mai day trip.",
                 "location": "Doi Inthanon National Park, Chom Thong, Chiang Mai", "cost": int(total*0.04), "rating": 4.7, "reviews_count": 640},
                {"activity": "Thai Cooking Class, Chiang Mai",
                 "description": "Join a morning market visit followed by a hands-on Thai cooking class — learn to make Pad Thai, Tom Yum Goong, and Mango Sticky Rice.",
                 "location": "Siam Rice Cooking School, Nimman Road, Chiang Mai", "cost": int(total*0.04), "rating": 4.8, "reviews_count": 520},
            ],
            "food": [
                {"name": "Jay Fai Street Food, Bangkok", "type": "Michelin-starred Street Thai — Crab Omelette", "cost_rating": "Medium"},
                {"name": "Khao San Road Night Market", "type": "Street Food — Pad Thai, Mango Sticky Rice", "cost_rating": "Budget"},
                {"name": "Le Normandie, Mandarin Oriental Bangkok", "type": "French Fine Dining with Chao Phraya Views", "cost_rating": "Luxury"},
            ],
            "transport": {
                "local_commute": "BTS Skytrain and MRT Metro in Bangkok. Grab (SE Asia's Uber) is reliable and cheap. Long-tail boats for canals.",
                "interstate_commute": "Suvarnabhumi Airport (BKK) and Don Mueang (DMK) serve Bangkok. AirAsia has cheap domestic flights to Phuket/Chiang Mai."
            },
            "tips": [
                "Dress respectfully at temples — cover shoulders and knees (scarves available at entry).",
                "Always carry small baht bills for street food and tuk-tuks.",
                "Book accommodation 2–3 months early for Dec–Jan peak season."
            ]
        },
        "dubai": {
            "lat": 25.2048, "lon": 55.2708,
            "activities": [
                {"activity": "Burj Khalifa At the Top (SKY)",
                 "description": "Take the world's fastest elevator to the 148th-floor observation deck for a 360° view of Dubai's skyline, the Palm, and the Arabian Desert.",
                 "location": "Burj Khalifa, 1 Sheikh Mohammed Bin Rashid Blvd, Downtown Dubai", "cost": int(total*0.06), "rating": 4.8, "reviews_count": 1100},
                {"activity": "Dubai Creek & Gold/Spice Souk",
                 "description": "Take an abra (wooden ferry) across the historic Dubai Creek. Browse the Gold Souk's 300+ jewellers and the aromatic Spice Souk nearby.",
                 "location": "Deira Gold Souk & Spice Souk, Dubai Creek, Deira", "cost": int(total*0.03), "rating": 4.7, "reviews_count": 850},
                {"activity": "Desert Safari & BBQ Dinner",
                 "description": "Experience dune bashing in a 4×4, sandboarding, camel rides, henna art, and a traditional BBQ dinner with belly dance performance under the stars.",
                 "location": "Dubai Desert Conservation Reserve, Al Maha, Dubai", "cost": int(total*0.08), "rating": 4.8, "reviews_count": 980},
                {"activity": "Palm Jumeirah & The Pointe Walk",
                 "description": "Walk across the iconic man-made palm island and visit The Pointe for views of Atlantis The Palm hotel and the Arabian Gulf.",
                 "location": "Palm Jumeirah & The Pointe, Palm Jumeirah, Dubai", "cost": int(total*0.02), "rating": 4.7, "reviews_count": 760},
                {"activity": "Dubai Mall & Dubai Fountain Show",
                 "description": "Explore the world's largest mall and watch the spectacular Dubai Fountain — 275m of water jets dancing to music under the Burj Khalifa every 30 minutes.",
                 "location": "The Dubai Mall & Dubai Fountain, Downtown Dubai", "cost": 0, "rating": 4.7, "reviews_count": 1050},
            ],
            "food": [
                {"name": "Al Ustad Special Kabab, Deira", "type": "Authentic Iranian Kebabs — Dubai Institution", "cost_rating": "Budget"},
                {"name": "Pierchic, Al Qasr Hotel", "type": "Overwater Seafood Fine Dining — Burj Al Arab Views", "cost_rating": "Luxury"},
                {"name": "Ravi Restaurant, Satwa", "type": "Pakistani Street Food — Legendary since 1978", "cost_rating": "Budget"},
            ],
            "transport": {
                "local_commute": "Dubai Metro Red/Green Lines cover major attractions. Careem or taxis for everything else. Monorail on Palm Jumeirah.",
                "interstate_commute": "Dubai International Airport (DXB) is a global hub with direct flights to 200+ cities via Emirates and FlyDubai."
            },
            "tips": [
                "Dress modestly in malls and public spaces — beachwear only at beaches and hotel pools.",
                "Download the RTA Dubai app for metro tickets and real-time route planning.",
                "Alcohol is served only in licensed hotel restaurants and bars — not in public."
            ]
        },
    }

    # ── Match destination to database (flexible keyword matching) ─────────────
    dest_data = None
    for key, data in DEST_DATA.items():
        if key in dest_lower or dest_lower in key:
            dest_data = data
            break

    # ── Fallback for unrecognised destinations ────────────────────────────────
    if dest_data is None:
        dest_title = destination.title()
        dest_data = {
            "lat": 28.6139, "lon": 77.2090,
            "activities": [
                {"activity": f"Explore {dest_title} Heritage Quarter",
                 "description": f"Walk through the historic heart of {dest_title}, visiting centuries-old architecture, local bazaars, and landmarks that define the city's character.",
                 "location": f"Heritage Quarter, {dest_title} City Centre", "cost": int(total*0.02), "rating": 4.5, "reviews_count": 420},
                {"activity": f"{dest_title} Iconic Landmark Tour",
                 "description": f"Visit the most famous and well-known tourist landmark of {dest_title} — a must-see attraction that captures the spirit of this destination.",
                 "location": f"Main Landmark, {dest_title}", "cost": int(total*0.04), "rating": 4.6, "reviews_count": 580},
                {"activity": "Local Street Food & Culinary Walk",
                 "description": f"Taste {dest_title}'s signature street food, local snacks, and regional specialities at the most popular food street in the city.",
                 "location": f"Food Street & Local Market, {dest_title}", "cost": int(total*0.03), "rating": 4.4, "reviews_count": 360},
                {"activity": "Scenic Viewpoint & Sunset Photography",
                 "description": f"Drive to the best viewpoint near {dest_title} for a panoramic sunset view of the landscape, city skyline, or natural scenery.",
                 "location": f"Hilltop Viewpoint, {dest_title} Outskirts", "cost": 0, "rating": 4.5, "reviews_count": 310},
                {"activity": "Nature Reserve & Garden Walk",
                 "description": f"Spend a relaxed morning walking through {dest_title}'s most famous natural park or garden — perfect for photography and peace.",
                 "location": f"Nature Reserve / Botanical Garden, {dest_title}", "cost": int(total*0.02), "rating": 4.4, "reviews_count": 280},
                {"activity": "Regional Museum & Cultural Experience",
                 "description": f"Dive into {dest_title}'s history and culture at the regional museum. Discover artefacts, art and stories that shaped this destination.",
                 "location": f"Regional Museum, {dest_title}", "cost": int(total*0.02), "rating": 4.3, "reviews_count": 240},
            ],
            "food": [
                {"name": f"The {dest_title} Kitchen", "type": "Traditional Local Cuisine & Regional Specialities", "cost_rating": "Medium"},
                {"name": "Street Food Corner", "type": "Local Snacks & Fast Bites", "cost_rating": "Budget"},
            ],
            "transport": {
                "local_commute": f"Use local auto-rickshaws or app-based cabs (Ola/Uber) in {dest_title}. Negotiate fares for tourist spots.",
                "interstate_commute": f"Book train or flight tickets 3–4 weeks in advance for the best fares to {dest_title}."
            },
            "tips": [
                f"Start your day early to beat the crowds at popular tourist spots in {dest_title}.",
                "Keep cash handy — small vendors and local transport may not accept digital payments.",
                f"Respect local customs and dress codes when visiting religious sites in {dest_title}."
            ]
        }

    dest_title = destination.title()
    act_pool   = dest_data["activities"]
    food_list  = dest_data["food"]
    time_slots = [
        "09:00 AM (Morning)", 
        "11:30 AM (Mid-Morning)", 
        "02:00 PM (Afternoon)", 
        "05:00 PM (Evening)", 
        "08:00 PM (Night)"
    ]

    day_wise = []
    for d in range(1, days + 1):
        acts_for_day = []
        for slot_i in range(5):
            pool_idx = ((d - 1) * 5 + slot_i) % len(act_pool)
            act = act_pool[pool_idx].copy()
            act["time"] = time_slots[slot_i]
            acts_for_day.append(act)

        food_for_day = [food_list[(d - 1) % len(food_list)], food_list[d % len(food_list)]]

        day_wise.append({
            "day": d,
            "title": f"Day {d} — Exploring {dest_title}",
            "activities": acts_for_day,
            "food_recommendations": food_for_day
        })

    return {
        "is_mock": True,
        "trip_overview": {
            "destination": dest_title,
            "days": days,
            "budget": budget,
            "theme": prefs_str
        },
        "day_wise_itinerary": day_wise,
        "budget_breakdown": {
            "hotel": hotel_cost,
            "food": food_cost,
            "transportation": trans_cost,
            "attractions_activities": attr_cost,
            "shopping_misc": misc_cost,
            "total_estimated_cost": int(total)
        },
        "transport_suggestions": dest_data["transport"],
        "essential_tips": dest_data["tips"]
    }


def generate_itinerary(destination: str, days: int, budget: float, preferences: List[str], api_key: str = None) -> Dict[str, Any]:
    """
    Generates a highly personalized, budget-conscious travel itinerary using Google Gemini.
    Returns a structured dictionary matching our travel schema.
    """
    if not api_key:
        return get_demo_itinerary(destination, days, budget, preferences)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prefs_str = ", ".join(preferences) if preferences else "General Sightseeing"

    prompt = f"""
    You are an expert AI Travel Planner. Design a realistic, highly personalized, day-wise travel itinerary.

    Trip Specifications:
    - Destination: {destination}
    - Duration: {days} Days
    - Budget: ₹{budget:,.2f} INR (Total — hotels, food, local transport, attraction entries)
    - Preferences/Interests: {prefs_str}

    CRITICAL REQUIREMENT: You MUST provide EXACTLY 5 activities per day covering the following slots: 
    1. Morning (~09:00 AM)
    2. Mid-Morning (~11:30 AM)
    3. Afternoon (~02:00 PM)
    4. Evening (~05:00 PM)
    5. Night (~08:00 PM)

    Budget Sensitivities:
    - Low budget (under ₹15,000 INR for 3+ days): focus on free attractions, budget hostels, street food, cheap local transport.
    - Mid-range (₹15,000–₹50,000): suggest 2–3 star hotels, comfortable cafes, local cabs, mid-range activities.
    - Luxury (over ₹50,000): premium resorts, fine dining, private guides, exclusive activities.

    Output MUST be a single valid JSON object. Do NOT include markdown tags like ```json. Just plain JSON.

    JSON Schema:
    {{
      "trip_overview": {{
        "destination": "Name of the destination",
        "days": {days},
        "budget": {budget},
        "theme": "A short theme phrase based on user preferences"
      }},
      "day_wise_itinerary": [
        {{
          "day": 1,
          "title": "Short catchy title for the day",
          "activities": [
            {{
              "time": "e.g., 09:00 AM (Morning)",
              "activity": "Name of activity",
              "description": "Engaging 1-2 sentence description with helpful context.",
              "location": "Exact real landmark/place name with area/city",
              "cost": 500,
              "lat": 15.4989,
              "lon": 73.8278,
              "rating": 4.7,
              "reviews_count": 215
            }}
            // MUST provide exactly 5 activities here for the day.
          ],
          "food_recommendations": [
            {{
              "name": "Exact restaurant/cafe/street food stall name",
              "type": "Cuisine type",
              "cost_rating": "Budget or Medium or Luxury"
            }}
          ]
        }}
      ],
      "budget_breakdown": {{
        "hotel": 6000,
        "food": 5000,
        "transportation": 4000,
        "attractions_activities": 3000,
        "shopping_misc": 2000,
        "total_estimated_cost": 20000
      }},
      "transport_suggestions": {{
        "local_commute": "Specific advice on local travel within this destination",
        "interstate_commute": "Advice on reaching this destination"
      }},
      "essential_tips": [
        "Useful tip 1 tailored to the location and budget",
        "Useful tip 2 tailored to the location and budget",
        "Useful tip 3 tailored to the location and budget"
      ]
    }}

    IMPORTANT:
    - All 'location' fields MUST be exact, real landmark names with their area/neighbourhood (e.g. "Amber Fort, Amer, Jaipur" not just "Fort").
    - Provide realistic lat/lon coordinates for every activity.
    - 'rating' must be between 4.0 and 5.0; 'reviews_count' between 25 and 1200.
    - Budget breakdown sum must not exceed ₹{budget}.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        itinerary_data = json.loads(response.text)
        itinerary_data["is_mock"] = False
        return itinerary_data

    except json.JSONDecodeError as je:
        print(f"JSON Parsing Error: {je}")
        text_clean = response.text.strip()
        if text_clean.startswith("```json"):
            text_clean = text_clean[7:]
        if text_clean.endswith("```"):
            text_clean = text_clean[:-3]
        try:
            return json.loads(text_clean.strip())
        except Exception:
            return get_demo_itinerary(destination, days, budget, preferences)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return get_demo_itinerary(destination, days, budget, preferences)


if __name__ == "__main__":
    print("Testing Mock Itinerary Generator...")
    it = get_demo_itinerary("Jaipur", 3, 15000, ["historical", "shopping"])
    print(json.dumps(it, indent=2))
