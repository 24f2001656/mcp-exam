
import hashlib
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.lowlevel.server import request_ctx

EMAIL = "24f2001656@ds.study.iitm.ac.in"

mcp = FastMCP(
    "Exam Challenge Server",
    stateless_http=True,
    json_response=True,
)

@mcp.tool()
def solve_challenge() -> str:
    """Return the hash of the challenge from HTTP headers."""

    request = request_ctx.get().request
    challenge = request.headers.get("x-exam-challenge", "")

    if len(challenge) != 32 or any(
        c not in "0123456789abcdef" for c in challenge
    ):
        raise ValueError("Invalid X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL}"
    return hashlib.sha256(message.encode()).hexdigest()[:16]


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http")

