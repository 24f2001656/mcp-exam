
import hashlib
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.lowlevel.server import request_ctx
from mcp.server.transport_security import TransportSecuritySettings

# Registered exam email
EMAIL = "24f2001656@ds.study.iitm.ac.in".strip().lower()

# Public Render hostname
RENDER_HOST = "mcp-exam-h7nq.onrender.com"

# Initialize MCP server
mcp = FastMCP(
    "Exam Challenge Server",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            RENDER_HOST,
            f"{RENDER_HOST}:*",
            "localhost:*",
            "127.0.0.1:*",
        ],
        allowed_origins=[
            f"https://{RENDER_HOST}",
        ],
    ),
)


# Register exactly one MCP tool
@mcp.tool()
def solve_challenge() -> str:
    """
    Read X-Exam-Challenge from the HTTP headers.
    Return the first 16 lowercase hexadecimal characters
    of SHA-256(challenge:email).
    """

    # Access the active HTTP request
    request = request_ctx.get().request

    # Read challenge from HTTP header
    challenge = request.headers.get("x-exam-challenge", "")

    # Validate challenge format
    if len(challenge) != 32 or any(
        c not in "0123456789abcdef" for c in challenge
    ):
        raise ValueError("Invalid X-Exam-Challenge header")

    # Construct required message
    message = f"{challenge}:{EMAIL}"

    # Calculate SHA-256
    digest = hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()

    # Return first 16 lowercase hexadecimal characters
    return digest[:16]


# Start MCP HTTP server
if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.environ.get("PORT", "8000"))

    mcp.run(transport="streamable-http")

