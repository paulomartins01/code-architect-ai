"""
Configuration Schema and Validator
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml


@dataclass
class ChunkingConfig:
    strategy: str = "smart"
    chunk_size: int = 1500
    chunk_overlap: int = 200
    respect_code_structure: bool = True


@dataclass
class EmbeddingConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    batch_size: int = 100
    max_retries: int = 3
    timeout: int = 30
    cache_folder: Optional[str] = None  # For local embeddings
    use_gpu: bool = True  # For local embeddings


@dataclass
class PathsConfig:
    source_code: str = "./src-to-analyze"
    output_dir: str = "./output"
    vector_store: str = "./output/vectorstore"
    export_file: str = "./output/cortex_knowledge_base.json"


@dataclass
class CodeProcessingConfig:
    extensions: List[str] = field(default_factory=lambda: [".js", ".jsx", ".ts", ".tsx"])
    ignore_dirs: List[str] = field(default_factory=lambda: ["node_modules", ".git"])
    ignore_files: List[str] = field(default_factory=lambda: ["package-lock.json"])
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)


@dataclass
class Config:
    """Main configuration class"""
    paths: PathsConfig
    code_processing: CodeProcessingConfig
    embedding: EmbeddingConfig
    project: Dict
    metadata: Dict
    architecture: Dict
    export: Dict
    logging: Dict
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract embedding config and filter valid fields
        embedding_data = data.get('embedding', {})
        embedding_config = {
            k: v for k, v in embedding_data.items()
            if k in ['provider', 'model', 'batch_size', 'max_retries', 'timeout', 'cache_folder', 'use_gpu']
        }
        
        return cls(
            project=data.get('project', {}),
            paths=PathsConfig(**data.get('paths', {})),
            code_processing=CodeProcessingConfig(
                extensions=data['code_processing']['extensions'],
                ignore_dirs=data['code_processing']['ignore_dirs'],
                ignore_files=data['code_processing']['ignore_files'],
                chunking=ChunkingConfig(**data['code_processing']['chunking'])
            ),
            embedding=EmbeddingConfig(**embedding_config),
            metadata=data.get('metadata', {}),
            architecture=data.get('architecture', {}),
            export=data.get('export', {}),
            logging=data.get('logging', {})
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not Path(self.paths.source_code).exists():
            raise ValueError(f"Source code path does not exist: {self.paths.source_code}")
        
        if self.code_processing.chunking.chunk_size < 100:
            raise ValueError("Chunk size must be at least 100")
        
        return True

