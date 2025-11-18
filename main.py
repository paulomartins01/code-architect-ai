#!/usr/bin/env python3
"""
CodeArchitect AI - Cortex Agent Builder
Main entry point
"""
import sys
from pathlib import Path
import argparse
from dotenv import load_dotenv

from config.config_schema import Config
from src.core.vectorizer import CodeVectorizer
from src.exporters.vector_exporter import VectorExporter
from src.utils.logger import CortexLogger


def main():
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='🏗️  CodeArchitect AI - Build Gaudí knowledge base from your codebase'
    )
    parser.add_argument(
        '--config',
        default='config/default.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--source',
        help='Source code directory (overrides config)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (overrides config)'
    )
    parser.add_argument(
        '--skip-embeddings',
        action='store_true',
        help='Skip embedding generation (faster, for testing)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Analyze without generating embeddings or exporting'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config.from_yaml(args.config)
    except Exception as e:
        print(f"[ERROR] Configuration error: {str(e)}")
        sys.exit(1)
    
    # Override with CLI args
    if args.source:
        config.paths.source_code = args.source
    if args.output:
        config.paths.export_file = args.output
    
    # Validate after applying CLI overrides
    try:
        config.validate()
    except Exception as e:
        print(f"[ERROR] Validation error: {str(e)}")
        sys.exit(1)
    
    # Initialize logger
    agent_name = config.project.get('agent_name', 'Cortex')
    logger = CortexLogger(agent_name, config.logging)
    
    logger.info("=" * 60)
    logger.info(f"🏗️  {config.project['name']} v{config.project['version']}")
    logger.info(f"🤖 Agent: {agent_name}")
    logger.info("=" * 60)
    
    try:
        # Initialize vectorizer
        vectorizer = CodeVectorizer(config, logger)
        
        # Process codebase
        chunks = vectorizer.process_codebase()
        
        if args.dry_run:
            logger.info("🔍 Dry run complete")
            logger.info(f"Stats: {vectorizer.get_stats()}")
            return
        
        # Generate embeddings
        if not args.skip_embeddings:
            chunks = vectorizer.generate_embeddings(chunks)
        else:
            logger.warning("⚠️  Skipping embeddings generation")
        
        # Export
        exporter = VectorExporter(config, logger)
        output_file = exporter.export(chunks)
        
        logger.info("=" * 60)
        logger.success("🎉 Knowledge base creation complete!")
        logger.info(f"📄 Output: {output_file}")
        logger.info(f"📊 Stats: {vectorizer.get_stats()}")
        logger.info("=" * 60)
        logger.info("Next steps:")
        logger.info("1. Review the generated summary in output/gaudi_summary.md")
        logger.info("2. Upload the knowledge base to your agent builder")
        logger.info("3. Configure your agent with the suggested prompt")
        logger.info("4. Start asking architectural questions!")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

