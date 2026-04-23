"""
Test the listing generator engine with a sample Regina property.
Run from project root:  python test_engine.py
"""

from core import ListingEngine


def main():
    engine = ListingEngine()

    property_details = {
        "property_type": "Bungalow",
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 1150,
        "lot_size": "50x120 ft",
        "year_built": 1952,
        "neighbourhood": "Cathedral",
        "city": "Regina",
        "features": [
            "Refinished hardwood floors throughout",
            "Updated kitchen with quartz countertops",
            "Fully finished basement with rec room",
            "New high-efficiency furnace (2024)",
            "Large fenced backyard with mature trees",
            "Detached double garage",
        ],
        "tone": "family-friendly",
    }

    print("=" * 60)
    print("  LISTING GENERATOR — ENGINE TEST")
    print("=" * 60)

    print("\n📝 Generating listing description...\n")
    description = engine.generate(property_details)
    word_count = len(description.split())
    print(description)
    print(f"\n   Word count: {word_count}")

    print("\n" + "=" * 60)
    print("  GENERATING 2 VARIATIONS")
    print("=" * 60)

    variations = engine.generate_variations(property_details, count=2)
    for i, var in enumerate(variations, 1):
        wc = len(var.split())
        print(f"\n--- Variation {i} ({wc} words) ---\n")
        print(var)

    print("\n" + "=" * 60)
    print("  ✅ ENGINE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
