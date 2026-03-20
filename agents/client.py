"""
Shared client factory for all agent sessions.

Switches between AWS Bedrock and direct Anthropic API based on the
PROVIDER env var.  AnthropicBedrock uses the standard boto3 credential
chain (AWS_PROFILE, env vars, instance role) automatically.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

PROVIDER = os.getenv("PROVIDER", "bedrock").lower()
MODEL = os.environ["MODEL_ID"]

if PROVIDER == "bedrock":
    from anthropic import AnthropicBedrock
    client = AnthropicBedrock(aws_region=os.getenv("AWS_REGION", "us-east-1"))
else:
    from anthropic import Anthropic
    if os.getenv("ANTHROPIC_BASE_URL"):
        os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
    client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
