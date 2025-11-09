account_to_vertical = {
    # ✈️ Aviation — (Vertical Leader: Brandon Castillo)
    "Delta Air Lines": "Aviation",  # Brandon Castillo

    # 🚗 Automotive — (Vertical Leaders: Marvin Owens / John Mann Interim)
    "Ford Motor Company": "Automotive",        # Nick Mufarrah / Khalfani Towns
    "General Motors": "Automotive",            # Robert Wallen
    "Tesla Inc.": "Automotive",                # Jacob Reed
    "Honda Motor Company": "Automotive",       # Greyson Wolff / Zach Kuebler
    "Detroit Diesel (DDC)": "Automotive",      # Robert Wallen (GM/DDC)

    # 🏭 Manufacturing — (Vertical Leaders: Ayesha Nasir / Aaron Simpson / Kim Wittekind)
    "Lockheed Martin": "Manufacturing",        # Michelle Bickford / Ben Ehrenberg
    "Boeing Company": "Manufacturing",         # Justin Dallavis
    "Northrop Grumman": "Manufacturing",       # Jennifer Segovia
    "Hewlett-Packard": "Manufacturing",        # Mark Schlerf / Jose Torres
    "Textron Aviation": "Manufacturing",       # Manufacturing cluster
    "Spirit Aerosystems": "Manufacturing",     # Manufacturing cluster
    "United Technologies": "Manufacturing",    # Manufacturing cluster
    "Mars": "Manufacturing",                   # Aaron Simpson (3M, Ball Corp, Mars)
    "Ball Corp": "Manufacturing",              # Aaron Simpson
    "Procter & Gamble Company": "Manufacturing", # Dustin Smith / Brent Taylor
    "GE Healthcare": "Manufacturing",          # Kim Wittekind
    "General Electric": "Manufacturing",       # Kim Wittekind (GE Aerospace)
    "General Dynamics": "Manufacturing",       # Jennifer Segovia
    "Nestle": "Manufacturing",                 # Kim Wittekind
    "Westinghouse": "Manufacturing",           # Ayesha Nasir
    "Micron Tech": "Manufacturing",            # Siddarth Shah (Manufacturing vertical)

    # 💻 Technology — (Vertical Leaders: Dan Hartman / Ryan Blackwood)
    "Microsoft": "Technology",                 # Shane Follmann / Taylor Wattenberg / Ivan Taminez
    "Meta": "Technology",                      # Luna Duarte / Grant Frazier
    "Intel": "Technology",                     # Jeremy Johnson / Alex Kennedy
    "Amazon": "Technology",                    # Keith Deuber / Dustin Smith (Global Accounts)
    "Amazon Office": "Technology",             # Sub-account of Amazon Global Accounts
    "Google": "Technology",                    # Ryan Blackwood / Caren Courtney / Ana Sabater
    "NVIDIA": "Technology",                    # Stuart Kelloff
    "Adobe Systems": "Technology",             # Zane Hauck / Stuart Kelloff
    "LinkedIn": "Technology",                  # Ryan Blackwood cluster
    "LAM Research": "Technology",              # Mark Schlerf / Jose Torres
    "IBM": "Technology",                       # IBM – Technology vertical cluster
    "Uber": "Technology",                      # ✅ Ryan Blackwood / Ana Sabater
    # note: LAM Research verified in Technology section of PDF

    # 💊 Life Science — (Vertical Leader: Dan Hartman)
    "Merck": "Life Science",                   # Brian Davis / Dave Pergola / Justin Homa
    "Abbott Labs": "Life Science",             # Greg DeMedio
    "Amgen": "Life Science",                   # Thomas Mahoney
    "Eli Lilly": "Life Science",               # Sara Brake / Fern Garner
    "Sanofi": "Life Science",                  # Scott Kimball
    "Gilead Sciences": "Life Science",         # Josh Grady (Gilead/Kite)
    "Takeda Pharmaceutical": "Life Science",   # Luis Cabrera
    "Lonza Biologics": "Life Science",         # Jacqueline Maravilla
    "Bristol Myers Squibb": "Life Science",    # Mike Barry (BMS)
    "Bayer": "Life Science",                   # Isaac Calderon
    "Medtronic": "Life Science",               # Gisell Langelier / Dan Hartman
    "Biogen": "Life Science",                  # Ann McClellan
    "Boehringer Ingelheim": "Life Science",    # Zach Shock
    "Novartis": "Life Science",                # Mike Barry
    "Johnson & Johnson": "Life Science",       # Isaac Calderon
    "Johnson & Johnson - Puerto Rico": "Life Science", # Duplicate of J&J account
    "AbbVie": "Life Science",                  # Corey Wallace (Life Science vertical)

    # 💰 Finance — (Vertical Leaders: Peggy Shum / Tiffany Purifoy)
    "Wells Fargo": "Finance",                  # Colleen Doles / Eduardo Sanchez
    "Charles Schwab": "Finance",               # Tiffany Purifoy
    "Deutsche Bank": "Finance",                # Peggy Shum
    "CIGNA": "Finance",                        # Julie Bianchi
    "USAA": "Finance",                         # Nashir Carabali

    # 📦 Distribution — (Vertical Leader: TBD)
    "Nike": "Distribution",  # Includes DHL, GXO Relay, GXO Connect, NALC, Adapt locations

    # 🧪 R&D / Education / Other
    "Great American Ball Park": "R&D / Education / Other"  # Facilities / Other cluster
}

# Fuzzy matching dictionary - maps CSV variations to canonical account names
account_name_variations = {
    # Exact matches (case-insensitive handled separately)
    "Abbvie": "AbbVie",
    "abbvie": "AbbVie",
    "Merck Sodexo": "Merck",
    "merck sodexo": "Merck",
    "Ball Corp": "Ball Corp",
    "ball corp": "Ball Corp",
    "Cigna": "CIGNA",
    "cigna": "CIGNA",
    "GM Milford": "General Motors",
    "gm milford": "General Motors",
    "Grant frazier": "Meta",  # Data entry error - Grant Frazier is Meta AD
    "grant frazier": "Meta",
    "Micron (C&W)": "Micron Tech",
    "micron (c&w)": "Micron Tech",
    "Great American Ballpark": "Great American Ball Park",
    "great american ballpark": "Great American Ball Park",
    "Lam Research": "LAM Research",
    "lam research": "LAM Research",
    "P&G(JLL)": "Procter & Gamble Company",
    "p&g(jll)": "Procter & Gamble Company",
    "P&G": "Procter & Gamble Company",
    "p&g": "Procter & Gamble Company",
    "Microsoft Puget Sound": "Microsoft",
    "microsoft puget sound": "Microsoft",
    "Boeing": "Boeing Company",
    "boeing": "Boeing Company",
    "General Dynamics": "General Dynamics",
    "general dynamics": "General Dynamics",
    "JLL Northrop Grumman": "Northrop Grumman",  # Map to canonical name
    "Wells Fargo-JLL": "Wells Fargo",  # JLL managed Wells Fargo
    "wells fargo-jll": "Wells Fargo",
    "Abbottt": "Abbott Labs",  # Typo in CSV
    "abbottt": "Abbott Labs",
    "Abbott": "Abbott Labs",  # Variation
    "abbott": "Abbott Labs",
    "Johnson & Johnson JLL": "Johnson & Johnson",  # JLL managed J&J
    "johnson & johnson jll": "Johnson & Johnson",
    "Omnicom": None,  # Omit from dashboard
    
    # Nike accounts - all map to single Nike account
    "Nike/DHL": "Nike",
    "nike/dhl": "Nike",
    "Nike/GXO Relay": "Nike",
    "Nike/GXO Relay (California)": "Nike",
    "nike/gxo relay": "Nike",
    "Nike/GXO Connect": "Nike",
    "Nike/GXO  Connect": "Nike",  # Extra space
    "nike/gxo connect": "Nike",
    "Nike/NALC": "Nike",
    "nike/nalc": "Nike",
    "Nike/Adapt": "Nike",
    "nike/adapt": "Nike",
}
