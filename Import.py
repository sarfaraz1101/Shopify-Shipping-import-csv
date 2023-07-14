import csv
import requests
import json
from tqdm import tqdm

url = "https://shop.myshopify.com/admin/api/2023-07/graphql.json"
access_token = " , "  # Add Shopify Access Token

# Define the GraphQL mutation
mutation = """
mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile {
      id
      name
      profileLocationGroups {
        locationGroup {
          id
          locations(first: 5) {
            nodes {
              name
              address {
                country
              }
            }
          }
        }
        locationGroupZones(first: 3) {
          edges {
            node {
              zone {
                id
                name
                countries {
                  code {
                    countryCode
                  }
                  provinces {
                    code
                  }
                }
              }
            }
          }
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""

# Read data from CSV files
filenames = [
    "shipping_data_1.csv", "shipping_data_2.csv", "shipping_data_3.csv", "shipping_data_4.csv",
    "shipping_data_5.csv", "shipping_data_6.csv", "shipping_data_7.csv", "shipping_data_8.csv",
    "shipping_data_9.csv", "shipping_data_10.csv", "shipping_data_11.csv", "shipping_data_12.csv",
    "shipping_data_13.csv", "shipping_data_14.csv", "shipping_data_15.csv", "shipping_data_16.csv",
    "shipping_data_17.csv", "shipping_data_18.csv", "shipping_data_19.csv", "shipping_data_20.csv",
    "shipping_data_21.csv", "shipping_data_22.csv", "shipping_data_23.csv", "shipping_data_24.csv",
    "shipping_data_25.csv", "shipping_data_26.csv", "shipping_data_27.csv", "shipping_data_28.csv"
]

# Create the GraphQL request payload
variables = {
    "id": "gid://shopify/DeliveryProfile/123456789",   # Add DeliveryProfile ID
    "profile": {
        "name": "Profile Name",                        # Add Profile Name
        "locationGroupsToCreate": [
            {
                "locationsToAdd": ["gid://shopify/Location/123456789"],  # Add shopify Location ID
                "zonesToCreate": []
            }
        ]
    }
}

# Send the GraphQL request for each batch of sheets
for i in tqdm(range(0, len(filenames), 1), desc="Batches"):
    batch_filenames = filenames[i:i+1]
    batch_data_sets = []

    # Read data from CSV files in the current batch
    for filename in batch_filenames:
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            batch_data_sets.append([row for row in reader])

    # Create zones for each data set in the current batch
    for data in tqdm(batch_data_sets, desc="Data sets", leave=False):
        method_definitions = []
        for row in data:
            method_definition = {
                "name": row["Shipping method"],
                "rateDefinition": {
                    "price": {
                        "amount": float(row["Price"]),
                        "currencyCode": "USD"
                    }
                },
                "weightConditionsToCreate": [
                    {
                        "criteria": {
                            "unit": "KILOGRAMS",
                            "value": float(row["Minimum weight"])
                        },
                        "operator": "GREATER_THAN_OR_EQUAL_TO"
                    },
                    {
                        "criteria": {
                            "unit": "KILOGRAMS",
                            "value": float(row["Maximum weight"])
                        },
                        "operator": "LESS_THAN_OR_EQUAL_TO"
                    }
                ]
            }
            method_definitions.append(method_definition)

        zone = {
            "name": f"Zone{len(variables['profile']['locationGroupsToCreate'][0]['zonesToCreate']) + 1}",
            "countries": {
                "code": data[0]["Country code (ISO 2)"],
                "provinces": [{"code": row["Province code"]} for row in data]
            },
            "methodDefinitionsToCreate": method_definitions
        }

        # Append the zone to the GraphQL request payload
        variables["profile"]["locationGroupsToCreate"][0]["zonesToCreate"].append(zone)

    # Create the GraphQL request payload
    payload = {
        "query": mutation,
        "variables": variables
    }

    # Send the GraphQL request
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    response = requests.post(url, json=payload, headers=headers)

    # Handle the response
    try:
        response_data = response.json()
        if "errors" in response_data:
            # Handle GraphQL errors
            errors = response_data["errors"]
            for error in errors:
                if "message" in error:
                    print("GraphQL Error:", error["message"])
                else:
                    print("GraphQL Error:", error)
        else:
            # Extract the relevant data from the response
            delivery_profile_update = response_data.get("data", {}).get("deliveryProfileUpdate")
            if delivery_profile_update:
                profile = delivery_profile_update.get("profile")
                if profile:
                    print("Updated Profile ID:", profile.get("id"))
                    print("Updated Profile Name:", profile.get("name"))
                else:
                    print("Profile not found in the response.")
            else:
                print("deliveryProfileUpdate not found in the response.")
    except json.decoder.JSONDecodeError as e:
        # Handle JSONDecodeError
        print("JSONDecodeError:", e)
        print("Response Content:", response.content)
