"""
Advanced code analysis for React Native projects
"""
import re
from pathlib import Path
from typing import Dict, List, Optional


class ReactNativeAnalyzer:
    """Analyzes React Native code structure and patterns"""
    
    def __init__(self, config: dict):
        self.config = config
        self.architecture_config = config.get('architecture', {})
    
    def analyze_file(self, file_path: Path, content: str) -> Dict:
        """Comprehensive file analysis"""
        
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'extension': file_path.suffix,
            'lines_count': len(content.split('\n')),
            'size_bytes': len(content.encode('utf-8'))
        }
        
        # Extract various aspects
        if self.config.get('extract_imports'):
            metadata['imports'] = self._extract_imports(content)
        
        if self.config.get('extract_exports'):
            metadata['exports'] = self._extract_exports(content)
        
        if self.config.get('extract_components'):
            metadata['components'] = self._extract_components(content)
        
        if self.config.get('extract_functions'):
            metadata['functions'] = self._extract_functions(content)
        
        if self.config.get('detect_patterns'):
            metadata['patterns'] = self._detect_patterns(content)
        
        if self.config.get('calculate_complexity'):
            metadata['complexity'] = self._calculate_complexity(content)
        
        if self.architecture_config.get('detect_layers'):
            metadata['layer'] = self._detect_layer(file_path)
        
        if self.architecture_config.get('map_features'):
            metadata['feature'] = self._detect_feature(file_path)
        
        return metadata
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        import_pattern = r'import\s+.*?from\s+[\'"](.+?)[\'"]'
        imports = re.findall(import_pattern, content)
        return list(set(imports))
    
    def _extract_exports(self, content: str) -> List[str]:
        """Extract export statements"""
        exports = []
        
        # Named exports
        named_pattern = r'export\s+(?:const|function|class)\s+(\w+)'
        exports.extend(re.findall(named_pattern, content))
        
        # Default export
        if 'export default' in content:
            exports.append('default')
        
        return exports
    
    def _extract_components(self, content: str) -> List[Dict]:
        """Extract React components"""
        components = []
        
        # Function components
        func_pattern = r'(?:export\s+)?(?:const|function)\s+([A-Z]\w+)\s*=?\s*\([^)]*\)\s*(?:=>)?\s*{'
        for match in re.finditer(func_pattern, content):
            components.append({
                'name': match.group(1),
                'type': 'functional'
            })
        
        # Class components
        class_pattern = r'class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?Component'
        for match in re.finditer(class_pattern, content):
            components.append({
                'name': match.group(1),
                'type': 'class'
            })
        
        return components
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names"""
        func_pattern = r'(?:const|function)\s+(\w+)\s*=?\s*(?:async\s*)?\([^)]*\)'
        functions = re.findall(func_pattern, content)
        return list(set(functions))
    
    def _detect_patterns(self, content: str) -> List[str]:
        """Detect common patterns"""
        patterns = []
        
        if 'useState' in content or 'useEffect' in content:
            patterns.append('hooks')
        
        if 'StyleSheet.create' in content:
            patterns.append('stylesheet')
        
        if 'useNavigation' in content or 'navigation.' in content:
            patterns.append('navigation')
        
        if 'useSelector' in content or 'useDispatch' in content:
            patterns.append('redux')
        
        if 'createContext' in content or 'useContext' in content:
            patterns.append('context')
        
        if re.search(r'test\(|describe\(|it\(', content):
            patterns.append('test')
        
        if 'fetch(' in content or 'axios.' in content:
            patterns.append('api-call')
        
        return patterns
    
    def _calculate_complexity(self, content: str) -> str:
        """Calculate code complexity (simplified)"""
        lines = len(content.split('\n'))
        functions = len(self._extract_functions(content))
        conditionals = content.count('if ') + content.count('switch ') + content.count('? ')
        
        score = (lines / 100) + (functions * 2) + (conditionals * 1.5)
        
        if score < 10:
            return 'low'
        elif score < 30:
            return 'medium'
        else:
            return 'high'
    
    def _detect_layer(self, file_path: Path) -> str:
        """Detect architectural layer"""
        path_str = str(file_path).lower()
        
        layers = self.architecture_config.get('layers', {})
        
        for layer_name, keywords in layers.items():
            if any(keyword in path_str for keyword in keywords):
                return layer_name
        
        return 'unknown'
    
    def _detect_feature(self, file_path: Path) -> Optional[str]:
        """Detect feature/domain from path"""
        parts = file_path.parts
        
        # Common feature folders
        feature_indicators = ['features', 'modules', 'screens', 'pages']
        
        for i, part in enumerate(parts):
            if part in feature_indicators and i + 1 < len(parts):
                return parts[i + 1]
        
        return None

