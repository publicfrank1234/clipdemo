import weaviate
from processor.clip_embedding import generate_text_embedding

# Initialize Weaviate client
client = weaviate.Client("http://localhost:8080")

# Define schema for the index (class)
class_name = "VideoKeyframe"
schema = {
    "classes": [
        {
            "class": class_name,
            "vectorizer": "none",  # We are providing our own vectors
            "properties": [
                {"name": "metadata", "dataType": ["string[]"], "indexed": False},
                {"name": "timestamp", "dataType": ["number"], "indexed": True},
                {"name": "video_id", "dataType": ["string"], "indexed": True},
            ],
        }
    ]
}

schemas = client.schema.get()
print("Schema:", schemas)


# Recreate schema if it exists
if client.schema.exists(class_name):
    client.schema.delete_class(class_name)
client.schema.create(schema)

# Create schema if it doesn't exist
# if not client.schema.exists(class_name):
#     client.schema.create(schema)

# Function to save embeddings to Weaviate
def save_embeddings_to_weaviate(embeddings, timestamps, video_id, metadata=None):
    if len(embeddings) != len(timestamps):
        raise ValueError("Number of embeddings and timestamps must match.")
    
    for i, embedding in enumerate(embeddings):
        vector = embedding.tolist()
        data_object = {
            "metadata": metadata[i] if metadata else [],
            "timestamp": timestamps[i],
            "video_id": video_id,
        }
        # Correct usage of the create method
        client.data_object.create(
            data_object=data_object,  # Directly pass the properties dictionary here
            class_name="VideoKeyframe",  # Use the correct class name
            vector=vector,  # Pass the embedding vector
        )

# Function to query Weaviate for similar vectors or text within the same video
def query_weaviate(query_input, video_id, top_k=30):
    """
    Query Weaviate for frames similar to the input vector or text query within the same video.

    Args:
        query_input (list or str): Query vector (1D list of floats) or text query.
        video_id (str): Unique identifier for the video to restrict the query.
        top_k (int): Number of top results to return.

    Returns:
        list: A list of dictionaries containing metadata and timestamps of the closest matches.
    """
    # If query_input is a string, convert it to a vector
    if isinstance(query_input, str):
        query_input = generate_text_embedding(query_input)

    try:
        # Perform vector-based query with a filter for video_id
        result = client.query.get(class_name, ["metadata", "timestamp"]).with_near_vector(
            {"vector": query_input.tolist()}
        ).with_where(
            {"path": ["video_id"], "operator": "Equal", "valueString": video_id}
        ).with_limit(top_k).do()  # Request specific fields in `.get()`

        if "errors" in result:
            print(f"Query errors: {result['errors']}")
            return []

        # Parse results
        frames = []
        for obj in result["data"]["Get"][class_name]:
            frames.append({
                "timestamp": obj.get("timestamp", None),  # Graceful handling of missing fields
                "metadata": obj.get("metadata", []),
            })

        return frames
    except Exception as e:
        print(f"Error querying Weaviate: {e}")
        return []

# Example usage
# embeddings = np.random.rand(10, 512)
# timestamps = [i * 2 for i in range(10)]
# video_id = "video123"
# metadata = [{"info": f"frame-{i}"} for i in range(10)]
# save_embeddings_to_weaviate(embeddings, timestamps, video_id, metadata)

# query_text = "a person walking on a beach"
# result = query_weaviate(query_text, "video123", top_k=5)
# print("Query result:", result)
