#!/usr/bin/env python3
"""
geo-seo-claude: AI-powered GEO (Generative Engine Optimization) toolkit
using Claude as the backbone for content analysis and optimization.

This tool helps optimize content for AI-powered search engines and
generative AI responses by analyzing and improving geo-relevance signals.
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).parent))

from core.client import ClaudeClient
from core.runner import AgentRunner


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="geo-seo-claude",
        description="AI-powered GEO optimization toolkit using Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available agents:
  geo-content          Optimize content for generative engine visibility
  geo-schema           Generate and validate schema markup
  geo-ai-visibility    Analyze AI citation and visibility potential
  geo-platform         Platform-specific GEO analysis (ChatGPT, Perplexity, etc.)

Examples:
  %(prog)s --agent geo-content --input content.txt
  %(prog)s --agent geo-schema --url https://example.com
  %(prog)s --agent geo-ai-visibility --input article.md --output report.json
        """,
    )

    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        choices=["geo-content", "geo-schema", "geo-ai-visibility", "geo-platform"],
        help="The GEO agent to run",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input file (text, markdown, HTML)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL to analyze (alternative to --input)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output file (defaults to stdout)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-opus-4-5",
        help="Claude model to use (default: claude-opus-4-5)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments and raise errors for invalid combinations."""
    if not args.api_key:
        print(
            "Error: Anthropic API key is required. "
            "Set ANTHROPIC_API_KEY environment variable or use --api-key.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.input and not args.url:
        print(
            "Error: Either --input or --url must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.input and not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    """Main entry point for the geo-seo-claude CLI."""
    args = parse_args()
    validate_args(args)

    if args.verbose:
        print(f"[geo-seo-claude] Running agent: {args.agent}")
        print(f"[geo-seo-claude] Model: {args.model}")
        if args.input:
            print(f"[geo-seo-claude] Input: {args.input}")
        if args.url:
            print(f"[geo-seo-claude] URL: {args.url}")

    try:
        client = ClaudeClient(api_key=args.api_key, model=args.model)
        runner = AgentRunner(client=client, verbose=args.verbose)

        result = runner.run(
            agent_name=args.agent,
            input_file=args.input,
            url=args.url,
            output_format=args.format,
        )

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result, encoding="utf-8")
            if args.verbose:
                print(f"[geo-seo-claude] Output written to: {args.output}")
        else:
            print(result)

        return 0

    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
