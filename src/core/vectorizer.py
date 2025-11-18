"""
Main vectorizer class - Core of CodeArchitect AI
"""
from pathlib import Path
from typing import List, Dict, Optional
import time
import os

from ..utils.logger import CortexLogger
from .code_analyzer import ReactNativeAnalyzer
from .chunk_strategy import SmartCodeChunker


class CodeVectorizer:
    """Main vectorization engine"""
    
    def __init__(self, config, logger: Optional[CortexLogger] = None):
        self.config = config
        # Use agent name from config, fallback to "Cortex"
        agent_name = config.project.get('agent_name', 'Cortex')
        self.logger = logger or CortexLogger(agent_name, config.logging)
        
        # Initialize components
        self.analyzer = ReactNativeAnalyzer(config.metadata)
        self.chunker = SmartCodeChunker(
            chunk_size=config.code_processing.chunking.chunk_size,
            overlap=config.code_processing.chunking.chunk_overlap
        )
        
        # Initialize embedding client based on provider
        self.embedding_provider = config.embedding.provider
        
        if self.embedding_provider == "local":
            self.logger.info("🆓 Initializing LOCAL embeddings (no API key needed)")
            from .local_embeddings import LocalEmbeddings
            
            model_name = config.embedding.model
            cache_folder = config.embedding.cache_folder or './models'
            
            self.embedder = LocalEmbeddings(
                model_name=model_name,
                cache_folder=cache_folder
            )
            
            model_info = self.embedder.get_model_info()
            self.logger.info(f"   📐 Dimensions: {model_info['dimensions']}")
            self.logger.info(f"   ⚡ Speed: {model_info['speed']}")
            self.logger.info(f"   🎯 Quality: {model_info['quality']}")
            
        elif self.embedding_provider == "openai":
            self.logger.info("☁️  Initializing OpenAI embeddings")
            from openai import OpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment. "
                    "Please set it in .env file or use provider: local"
                )
            
            self.embedder = OpenAI(api_key=api_key)
            self.logger.info(f"   🤖 Model: {config.embedding.model}")
            
        else:
            raise ValueError(
                f"Unknown embedding provider: {self.embedding_provider}. "
                f"Supported: 'local', 'openai'"
            )
        
        self.stats = {
            'files_processed': 0,
            'chunks_created': 0,
            'errors': 0,
            'embedding_provider': self.embedding_provider
        }
    
    def process_codebase(self, source_path: Optional[str] = None) -> List[Dict]:
        """Process entire codebase"""
        source_path = source_path or self.config.paths.source_code
        root = Path(source_path)
        
        self.logger.info(f"🚀 Starting codebase analysis: {root}")
        self.logger.info(f"🤖 Agent: {self.config.project['agent_name']}")
        
        all_chunks = []
        start_time = time.time()
        
        # Scan files
        files = self._scan_files(root)
        self.logger.info(f"📁 Found {len(files)} files to process")
        
        # Process each file
        for file_path in files:
            try:
                chunks = self._process_file(file_path)
                all_chunks.extend(chunks)
                self.stats['files_processed'] += 1
                
                if self.stats['files_processed'] % 10 == 0:
                    self.logger.processing(
                        f"Processed {self.stats['files_processed']}/{len(files)} files"
                    )
            
            except Exception as e:
                self.stats['errors'] += 1
                self.logger.error(f"Error processing {file_path}: {str(e)}")
        
        elapsed = time.time() - start_time
        self.stats['chunks_created'] = len(all_chunks)
        
        self.logger.success(
            f"Processing complete! {self.stats['files_processed']} files, "
            f"{self.stats['chunks_created']} chunks in {elapsed:.2f}s"
        )
        
        return all_chunks
    
    def _scan_files(self, root: Path) -> List[Path]:
        """Scan for relevant files"""
        files = []
        extensions = set(self.config.code_processing.extensions)
        ignore_dirs = set(self.config.code_processing.ignore_dirs)
        ignore_files = set(self.config.code_processing.ignore_files)
        
        for file_path in root.rglob('*'):
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in ignore_dirs):
                continue
            
            # Skip ignored files
            if file_path.name in ignore_files:
                continue
            
            # Check extension
            if file_path.is_file() and file_path.suffix in extensions:
                files.append(file_path)
        
        return sorted(files)
    
    def _process_file(self, file_path: Path) -> List[Dict]:
        """Process a single file"""
        self.logger.debug(f"Processing: {file_path}")
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Analyze file
        metadata = self.analyzer.analyze_file(file_path, content)
        
        # Chunk content
        chunks = self.chunker.chunk(content, metadata)
        
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for all chunks"""
        self.logger.info(f"🧠 Generating embeddings for {len(chunks)} chunks")
        self.logger.info(f"   📡 Provider: {self.embedding_provider}")
        
        batch_size = self.config.embedding.batch_size
        enriched_chunks = []
        
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(chunks), batch_size):
            batch = chunks[batch_idx:batch_idx + batch_size]
            texts = [chunk['content'] for chunk in batch]
            
            current_batch = (batch_idx // batch_size) + 1
            
            try:
                if self.embedding_provider == "local":
                    # Local embeddings
                    self.logger.debug(f"Processing batch {current_batch}/{total_batches}...")
                    embeddings = self.embedder.embed_documents(texts)
                    
                    for chunk, embedding in zip(batch, embeddings):
                        enriched_chunks.append({
                            **chunk,
                            'embedding': embedding
                        })
                    
                elif self.embedding_provider == "openai":
                    # OpenAI API
                    self.logger.debug(f"Calling OpenAI API - batch {current_batch}/{total_batches}...")
                    response = self.embedder.embeddings.create(
                        model=self.config.embedding.model,
                        input=texts
                    )
                    
                    for chunk, embedding_data in zip(batch, response.data):
                        enriched_chunks.append({
                            **chunk,
                            'embedding': embedding_data.embedding
                        })
                
                # Progress update every 10 batches
                if current_batch % 10 == 0:
                    self.logger.processing(
                        f"Embeddings: {current_batch}/{total_batches} batches complete"
                    )
            
            except Exception as e:
                self.logger.error(
                    f"Error generating embeddings for batch {current_batch}: {str(e)}", 
                    exc_info=True
                )
                
                # For local, fail immediately (no retry)
                if self.embedding_provider == "local":
                    raise
                
                # For OpenAI, retry with exponential backoff
                import time
                for retry in range(self.config.embedding.max_retries):
                    try:
                        self.logger.warning(f"Retrying batch {current_batch} (attempt {retry + 1})...")
                        time.sleep(2 ** retry)  # Exponential backoff
                        
                        response = self.embedder.embeddings.create(
                            model=self.config.embedding.model,
                            input=texts
                        )
                        
                        for chunk, embedding_data in zip(batch, response.data):
                            enriched_chunks.append({
                                **chunk,
                                'embedding': embedding_data.embedding
                            })
                        break
                    except Exception as retry_e:
                        if retry == self.config.embedding.max_retries - 1:
                            self.logger.error(f"Failed after {retry + 1} retries")
                            raise retry_e
        
        self.logger.success(f"Generated {len(enriched_chunks)} embeddings")
        return enriched_chunks
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return self.stats

