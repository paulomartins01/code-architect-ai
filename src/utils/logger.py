"""
Logging utility for CodeArchitect AI
"""
import logging
import sys
from pathlib import Path


class CortexLogger:
    """Custom logger for CodeArchitect AI agent"""
    
    def __init__(self, name: str = "Cortex", config: dict = None):
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with handlers"""
        level = getattr(logging, self.config.get('level', 'INFO'))
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        if self.config.get('console_output', True):
            console_handler = logging.StreamHandler(sys.stdout)
            # Force UTF-8 encoding on Windows
            if sys.platform == 'win32' and hasattr(console_handler.stream, 'reconfigure'):
                try:
                    console_handler.stream.reconfigure(encoding='utf-8')
                except Exception:
                    pass  # If reconfigure fails, continue without it
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)
        
        # File handler
        log_file = self.config.get('file')
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)
    
    def _get_formatter(self):
        """Get formatter based on config"""
        format_type = self.config.get('format', 'detailed')
        
        if format_type == 'simple':
            return logging.Formatter('%(levelname)s: %(message)s')
        elif format_type == 'json':
            return logging.Formatter(
                '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
            )
        else:  # detailed
            return logging.Formatter(
                '%(asctime)s | 🏗️  %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def success(self, message: str):
        """Custom success level"""
        self.logger.info(f"✅ {message}")
    
    def processing(self, message: str):
        """Custom processing level"""
        self.logger.info(f"⚙️  {message}")

