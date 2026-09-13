# [C] Crawl4AI is Vulnerable to Remote Code Execution in Docker API via Hooks Parameter

## Summary
Severity: Critical
Advisory: GHSA-5882-5rx9-xgxp
CVE: CVE-2026-26216
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-5882-5rx9-xgxp
Type: github-advisory

## Affected
- PyPI: `Crawl4AI` — affected >=0 <0.8.0

## Details
A critical remote code execution vulnerability exists in the Crawl4AI Docker API deployment. The `/crawl` endpoint accepts a `hooks` parameter containing Python code that is executed using `exec()`. The `__import__` builtin was included in the allowed builtins, allowing attackers to import arbitrary modules and execute system commands.

**Attack Vector:**
```json
POST /crawl
{
  "urls": ["https://example.com"],
  "hooks": {
    "code": {
      "on_page_context_created": "async def hook(page, context, **kwargs):\n    __import__('os').system('malicious_command')\n    return page"
    }
  }
}
```

### Impact

An unauthenticated attacker can:
- Execute arbitrary system commands
- Read/write files on the server
- Exfiltrate sensitive data (environment variables, API keys)
- Pivot to internal network services
- Completely compromise the server

### Mitigation

1. **Upgrade to v0.8.0** (recommended)
2. If unable to upgrade immediately:
   - Disable the Docker API
   - Block `/crawl` endpoint at network level
   - Add authentication to the API

### Fix Details

1. Removed `__import__` from `allowed_builtins` in `hook_manager.py`
2. Hooks disabled by default (`CRAWL4AI_HOOKS_ENABLED=false`)
3. Users must explicitly opt-in to enable hooks

### Credits

Discovered by Neo by ProjectDiscovery (https://projectdiscovery.io)

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-5882-5rx9-xgxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-26216
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-33.yaml
- https://github.com/unclecode/crawl4ai
- https://github.com/unclecode/crawl4ai/blob/main/docs/blog/release-v0.8.0.md
- https://github.com/unclecode/crawl4ai/blob/release/v0.8.0/docs/blog/release-v0.8.0.md
- https://github.com/unclecode/crawl4ai/blob/release/v0.8.0/docs/migration/v0.8.0-upgrade-guide.md
- https://www.vulncheck.com/advisories/crawl4ai-docker-api-unauthenticated-remote-code-execution-via-hooks-parameter
