# [H] PraisonAI: PRAISONAI_CALL_AUTH=disabled environment variable unconditionally disables authentication

## Summary
Severity: High
Advisory: GHSA-8ccj-p46r-jwqq
CVE: CVE-2026-57132
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-8ccj-p46r-jwqq
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.61

## Details
### Summary
Setting `PRAISONAI_CALL_AUTH=disabled` completely disables all authentication on the `/api/v1/agents/{id}/invoke` endpoint. This bypass is advertised in the application's own error messages, making it likely to appear in production Docker and Compose configurations.

### Details

```python
# src/praisonai/praisonai/api/agent_invoke.py:32
_CALL_AUTH_DISABLED = os.getenv('PRAISONAI_CALL_AUTH', '').lower() == 'disabled'

async def verify_token(...) -> None:
    if _CALL_AUTH_DISABLED:
        return  # all authentication skipped unconditionally
```

The application's own error message advertises the bypass:
> "Set CALL_SERVER_TOKEN or PRAISONAI_CALL_AUTH=disabled to run without authentication."

This causes the setting to appear in Docker/Compose configurations as a convenience option.

### Proof of Concept

```python
import os
os.environ["PRAISONAI_CALL_AUTH"] = "disabled"
# verify_token() now returns immediately for any request
# POST /api/v1/agents/any-agent/invoke → 200 OK (no token needed)
```

Common vulnerable deployment:

```yaml
# docker-compose.yml
environment:
  - PRAISONAI_CALL_AUTH=disabled  # auth completely disabled
```

### Impact
Full unauthenticated access to the agent invocation API. Any agent registered on the server can be triggered without credentials, potentially executing arbitrary actions depending on the agent's configured tools.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8ccj-p46r-jwqq
- https://github.com/MervinPraison/PraisonAI
