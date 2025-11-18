"""
Local Embeddings - No API key required!
Uses sentence-transformers for local embedding generation.
"""
from sentence_transformers import SentenceTransformer
from typing import List
import torch
from pathlib import Path


class LocalEmbeddings:
    """Generate embeddings locally without API calls"""
    
    # Available models and their specs
    MODELS = {
        'all-MiniLM-L6-v2': {
            'dimensions': 384,
            'speed': 'fast',
            'quality': 'good',
            'size_mb': 80,
            'description': 'Best balance - fast and good quality'
        },
        'all-mpnet-base-v2': {
            'dimensions': 768,
            'speed': 'medium',
            'quality': 'excellent',
            'size_mb': 420,
            'description': 'Best quality - slower but more accurate'
        },
        'paraphrase-multilingual-MiniLM-L12-v2': {
            'dimensions': 384,
            'speed': 'fast',
            'quality': 'good',
            'size_mb': 420,
            'description': 'Multilingual support - good for Portuguese code comments'
        }
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_folder: str = None):
        """
        Initialize local embedding model
        
        Args:
            model_name: Name of the sentence-transformer model
            cache_folder: Where to cache downloaded models
        """
        self.model_name = model_name
        
        if model_name not in self.MODELS:
            available = ', '.join(self.MODELS.keys())
            raise ValueError(
                f"Model '{model_name}' not recognized. "
                f"Available: {available}"
            )
        
        print(f"🔄 Loading local model: {model_name}")
        print(f"   📊 {self.MODELS[model_name]['description']}")
        
        # Set cache folder if provided
        if cache_folder:
            Path(cache_folder).mkdir(parents=True, exist_ok=True)
        
        # Load model
        self.model = SentenceTransformer(
            model_name,
            cache_folder=cache_folder
        )
        
        # Use GPU if available
        self.device = 'cpu'
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')
            self.device = 'cuda'
            print("   🚀 GPU acceleration enabled")
        elif torch.backends.mps.is_available():
            self.model = self.model.to('mps')
            self.device = 'mps'
            print("   🚀 Apple Silicon acceleration enabled")
        else:
            print("   💻 Using CPU (slower but works)")
        
        print(f"   ✅ Model loaded successfully!")
        print(f"   📐 Embedding dimensions: {self.get_dimensions()}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Generate embeddings with progress bar
        embeddings = self.model.encode(
            texts,
            show_progress_bar=len(texts) > 10,  # Show only for large batches
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for better similarity
        )
        
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.tolist()
    
    def get_dimensions(self) -> int:
        """Get the dimension size of embeddings"""
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            'name': self.model_name,
            'device': self.device,
            'dimensions': self.get_dimensions(),
            **self.MODELS[self.model_name]
        }


# Backward compatibility wrapper for OpenAI-like interface
class LocalEmbeddingsWrapper:
    """Wrapper to make local embeddings compatible with OpenAI interface"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings = LocalEmbeddings(model_name)
    
    def create(self, input: List[str], model: str = None):
        """OpenAI-compatible create method"""
        embeddings = self.embeddings.embed_documents(input)
        
        # Return in OpenAI format
        class Response:
            def __init__(self, embeddings):
                self.data = [
                    type('obj', (object,), {'embedding': emb})
                    for emb in embeddings
                ]
        
        return Response(embeddings)

