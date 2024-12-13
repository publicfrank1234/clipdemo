from processor.weaviate import save_embeddings_to_weaviate
from processor.clip_embedding import generate_clip_embeddings
from processor.video_processing import extract_keyframes

def vectorize(video_path, video_id):
    # Step 1: Extract Keyframes
    keyframes, timeframes = extract_keyframes(video_path)

    # Step 2: Generate CLIP Embeddings
    embeddings = generate_clip_embeddings(keyframes)

    # Step 3: Save Embeddings to Pinecone
    save_embeddings_to_weaviate(embeddings, timeframes, video_id)

    print("Keyframes and embeddings saved to Weaviate.")
