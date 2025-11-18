"""
Intelligent code chunking strategies
"""
from typing import List, Dict
from pathlib import Path
import re


class ChunkStrategy:
    """Base class for chunking strategies"""
    
    def chunk(self, content: str, metadata: Dict) -> List[Dict]:
        raise NotImplementedError


class SmartCodeChunker(ChunkStrategy):
    """Smart chunking that respects code structure"""
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, content: str, metadata: Dict) -> List[Dict]:
        """Chunk code intelligently"""
        
        # Try to split by logical blocks first
        if metadata.get('extension') in ['.js', '.jsx', '.ts', '.tsx']:
            return self._chunk_javascript(content, metadata)
        else:
            return self._chunk_generic(content, metadata)
    
    def _chunk_javascript(self, content: str, metadata: Dict) -> List[Dict]:
        """Chunk JavaScript/TypeScript code"""
        chunks = []
        
        # Try to split by top-level constructs
        blocks = self._split_by_constructs(content)
        
        current_chunk = []
        current_size = 0
        
        for block in blocks:
            block_size = len(block)
            
            if current_size + block_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append(self._create_chunk(chunk_content, metadata, len(chunks)))
                
                # Start new chunk with overlap
                if self.overlap > 0 and current_chunk:
                    current_chunk = [current_chunk[-1], block]
                    current_size = len(current_chunk[-1]) + block_size
                else:
                    current_chunk = [block]
                    current_size = block_size
            else:
                current_chunk.append(block)
                current_size += block_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunks.append(self._create_chunk(chunk_content, metadata, len(chunks)))
        
        return chunks if chunks else [self._create_chunk(content, metadata, 0)]
    
    def _split_by_constructs(self, content: str) -> List[str]:
        """Split by functions, classes, exports"""
        
        # Split by double newlines first
        blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
        
        if not blocks:
            blocks = [content]
        
        return blocks
    
    def _chunk_generic(self, content: str, metadata: Dict) -> List[Dict]:
        """Generic chunking by lines"""
        lines = content.split('\n')
        chunks = []
        
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            
            if current_size + line_size > self.chunk_size and current_chunk:
                chunk_content = '\n'.join(current_chunk)
                chunks.append(self._create_chunk(chunk_content, metadata, len(chunks)))
                
                # Overlap
                overlap_lines = max(1, int(self.overlap / max(1, current_size / len(current_chunk))))
                current_chunk = current_chunk[-overlap_lines:] + [line]
                current_size = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(self._create_chunk(chunk_content, metadata, len(chunks)))
        
        return chunks if chunks else [self._create_chunk(content, metadata, 0)]
    
    def _create_chunk(self, content: str, metadata: Dict, index: int) -> Dict:
        """Create chunk with metadata"""
        chunk_metadata = metadata.copy()
        chunk_metadata['chunk_index'] = index
        chunk_metadata['chunk_size'] = len(content)
        
        # Add context header
        enhanced_content = f"""# File: {metadata.get('file_path', 'unknown')}
# Layer: {metadata.get('layer', 'unknown')}
# Feature: {metadata.get('feature', 'N/A')}
# Chunk: {index + 1}

{content}
"""
        
        return {
            'content': enhanced_content.strip(),
            'metadata': chunk_metadata
        }

