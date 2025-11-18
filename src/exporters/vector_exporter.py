"""
Export vectorized data to various formats
"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from ..utils.logger import CortexLogger


class VectorExporter:
    """Export vectorized codebase"""
    
    def __init__(self, config, logger: CortexLogger):
        self.config = config
        self.logger = logger
    
    def export(self, chunks: List[Dict]) -> str:
        """Export to configured format"""
        export_config = self.config.export
        
        if export_config['format'] == 'json':
            return self._export_json(chunks)
        elif export_config['format'] == 'jsonl':
            return self._export_jsonl(chunks)
        else:
            raise ValueError(f"Unsupported format: {export_config['format']}")
    
    def _export_json(self, chunks: List[Dict]) -> str:
        """Export as JSON"""
        output_file = Path(self.config.paths.export_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📦 Exporting to: {output_file}")
        
        # Prepare export data
        export_data = {
            'metadata': {
                'agent_name': self.config.project['agent_name'],
                'project_name': self.config.project['name'],
                'version': self.config.project['version'],
                'generated_at': datetime.now().isoformat(),
                'total_chunks': len(chunks),
                'embedding_model': self.config.embedding.model
            },
            'chunks': []
        }
        
        # Add chunks
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'id': f"chunk_{idx}",
                'content': chunk['content'],
                'metadata': chunk['metadata']
            }
            
            if self.config.export.get('include_embeddings', True):
                chunk_data['embedding'] = chunk.get('embedding', [])
            
            export_data['chunks'].append(chunk_data)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if self.config.export.get('pretty_print', True):
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(export_data, f, ensure_ascii=False)
        
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        self.logger.success(f"Exported {len(chunks)} chunks ({file_size:.2f} MB)")
        
        # Generate summary
        self._generate_summary(export_data, output_file.parent)
        
        return str(output_file)
    
    def _export_jsonl(self, chunks: List[Dict]) -> str:
        """Export as JSON Lines"""
        output_file = Path(self.config.paths.export_file).with_suffix('.jsonl')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                json.dump(chunk, f, ensure_ascii=False)
                f.write('\n')
        
        return str(output_file)
    
    def _generate_summary(self, export_data: Dict, output_dir: Path):
        """Generate summary report"""
        summary_file = output_dir / 'cortex_summary.md'
        
        chunks = export_data['chunks']
        
        # Calculate statistics
        layers = {}
        features = {}
        patterns = {}
        
        for chunk in chunks:
            metadata = chunk['metadata']
            
            layer = metadata.get('layer', 'unknown')
            layers[layer] = layers.get(layer, 0) + 1
            
            feature = metadata.get('feature')
            if feature:
                features[feature] = features.get(feature, 0) + 1
            
            for pattern in metadata.get('patterns', []):
                patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Generate markdown
        summary = f"""# 🏗️ {export_data['metadata']['agent_name']} Knowledge Base Summary

## Project Information
- **Agent**: {export_data['metadata']['agent_name']}
- **Project**: {export_data['metadata']['project_name']}
- **Generated**: {export_data['metadata']['generated_at']}
- **Total Chunks**: {export_data['metadata']['total_chunks']}
- **Embedding Model**: {export_data['metadata']['embedding_model']}

## Architecture Layers
| Layer | Chunks |
|-------|--------|
"""
        for layer, count in sorted(layers.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {layer} | {count} |\n"
        
        if features:
            summary += f"""
## Features Detected
| Feature | Chunks |
|---------|--------|
"""
            for feature, count in sorted(features.items(), key=lambda x: x[1], reverse=True)[:10]:
                summary += f"| {feature} | {count} |\n"
        
        if patterns:
            summary += f"""
## Patterns Found
| Pattern | Occurrences |
|---------|-------------|
"""
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                summary += f"| {pattern} | {count} |\n"
        
        summary += f"""
## Usage Instructions

### 1. Upload to Vector Database

Upload `{Path(self.config.paths.export_file).name}` to your agent builder's vector database.

### 2. Configure Agent Prompt

```
You are {export_data['metadata']['agent_name']}, an expert software architect specializing in React Native.

You have complete knowledge of our codebase through RAG (Retrieval Augmented Generation).

When providing architectural guidance:
- Consider existing patterns and conventions in the codebase
- Reference specific files and components when relevant
- Suggest improvements aligned with best practices
- Maintain consistency with current architecture
- Think about scalability and maintainability

Always ground your recommendations in the actual codebase structure.
```

### 3. Test Queries

Try asking:
- "What's our current architecture structure?"
- "How is navigation implemented?"
- "Suggest improvements for [specific feature]"
- "What patterns are we using for state management?"
- "Review the code organization and suggest improvements"

---
*Generated by CodeArchitect AI - Empowering architectural decisions with AI*
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        self.logger.success(f"Summary generated: {summary_file}")

