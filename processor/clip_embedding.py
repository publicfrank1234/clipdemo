import torch
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer

# Load CLIP model, processor, and tokenizer
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")

def generate_clip_embeddings(images):
    """
    Generate normalized image embeddings using the CLIP model.

    Args:
        images (list): List of images (e.g., PIL.Image objects or image arrays).

    Returns:
        torch.Tensor: Normalized image embeddings (shape: [num_images, embedding_dim]).
    """
    # Preprocess the images and prepare tensors
    inputs = processor(images=images, return_tensors="pt", padding=True)

    # Generate image embeddings
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    # Normalize embeddings to unit vectors
    embeddings = image_features / image_features.norm(dim=-1, keepdim=True)
    return embeddings

def generate_text_embedding(text):
    """
    Generate a normalized text embedding using the CLIP model.

    Args:
        text (str): Input text query.

    Returns:
        np.ndarray: Normalized text embedding vector.
    """
    # Preprocess the text and prepare tensors
    inputs = clip_tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # Generate text embeddings
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    # Normalize embeddings to unit vectors
    text_embeddings = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_embeddings.detach().numpy()[0]  # Convert to NumPy array
