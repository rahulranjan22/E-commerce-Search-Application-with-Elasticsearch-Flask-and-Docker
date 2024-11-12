import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers

# Elasticsearch connection setup
es = Elasticsearch(
    ["hostname:port"],
    basic_auth=("username", "password"),
)

# Define the index name
index_name = "products"

# Load product data from CSV
def load_data(file_path):
    return pd.read_csv(file_path, encoding='ISO-8859-1')  # Use the correct encoding

# Delete the index if it exists
def delete_index():
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted.")
    else:
        print(f"Index '{index_name}' does not exist.")

# Create the index with mappings if it doesn't exist
def create_index():
    index_config = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "ProductId": {"type": "keyword"},  # Unique identifier
                "Gender": {"type": "keyword"},  # Categorical value
                "Category": {"type": "keyword"},  # Categorical value
                "SubCategory": {"type": "keyword"},  # Categorical value
                "ProductType": {"type": "keyword"},  # Categorical value
                "Colour": {"type": "keyword"},  # Categorical value
                "Usage": {"type": "keyword"},  # Categorical value
                "ProductTitle": {"type": "text"},  # Text field, full-text search
                "Image": {"type": "keyword"},  # Image filename (can be used for filtering)
                "ImageURL": {"type": "keyword"}  # Image URL (can be used for filtering)
            }
        }
    }
    # Create the index with the new mappings
    es.indices.create(index=index_name, settings=index_config["settings"], mappings=index_config["mappings"])
    print(f"Created index '{index_name}' with mappings.")

# Bulk ingest data into Elasticsearch
def ingest_data(data):
    actions = [
        {
            "_index": index_name,
            "_source": {
                "ProductId": row["ProductId"],
                "Gender": row["Gender"],
                "Category": row["Category"],
                "SubCategory": row["SubCategory"],
                "ProductType": row["ProductType"],
                "Colour": row["Colour"],
                "Usage": row["Usage"],
                "ProductTitle": row["ProductTitle"],
                "Image": row["Image"],
                "ImageURL": row["ImageURL"]
            }
        }
        for _, row in data.iterrows()
    ]
    try:
        helpers.bulk(es, actions)
        print("Data ingested successfully.")
    except Exception as e:
        print(f"Error ingesting data: {e}")

# Main function
def main():
    # Load data from CSV file
    file_path = "fashion.csv"  # Update with the correct path if necessary
    data = load_data(file_path)
    
    # Delete the index if it already exists
    delete_index()
    
    # Create the index
    create_index()
    
    # Ingest data into Elasticsearch
    ingest_data(data)

if __name__ == "__main__":
    main()
