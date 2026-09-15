# [M] PraisonAI vulnerable to Server-Side Request Forgery via DNS rebinding bypass in webhook_url validation

## Summary
Severity: Medium
Advisory: GHSA-hmfx-4v44-9qw9
CVE: CVE-2026-55535
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-hmfx-4v44-9qw9
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
### Summary
The `webhook_url` field in the Jobs API silently passes validation when DNS resolution fails (`socket.gaierror`), enabling DNS rebinding attacks. An attacker's domain can initially resolve to a public IP (passing validation) then switch to an internal IP before the server makes the HTTP request.

### Details
The validator catches `socket.gaierror` and silently allows the URL:

```python
# src/praisonai/praisonai/jobs/models.py:55
try:
    ip = socket.gethostbyname(hostname)
    ip_obj = ipaddress.ip_address(ip)
    if ip_obj.is_private or ip_obj.is_loopback:
        raise ValueError("private address")
except socket.gaierror:
    pass  # BUG: DNS failure silently ignored → SSRF bypass
```

The HTTP call is made later with no re-validation:

```python
# src/praisonai/praisonai/jobs/executor.py:402
async with httpx.AsyncClient() as client:
    await client.post(job.webhook_url, ...)  # no second IP check
```

### Proof of Concept

**DNS rebinding flow:**
1. Register `attacker.com` with TTL=1s → resolves to `1.2.3.4` (public IP)
2. Submit job: `webhook_url=http://attacker.com/callback`
3. Validation passes (public IP)
4. Switch DNS: `attacker.com` → `127.0.0.1`
5. Job completes → server POSTs to `127.0.0.1` → internal SSRF

**Unresolvable domain bypass (no DNS rebinding required):**

```bash
curl -X POST http://:8005/api/v1/runs \
  -d '{"prompt":"run","webhook_url":"http://unresolvable.internal/cb","agent_yaml":"..."}'
# Validation: gaierror → pass → URL accepted
```

### Impact
SSRF to internal HTTP services: admin panels, databases, and cloud metadata APIs (e.g., `http://169.254.169.254/`). Exploitable without authentication.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-hmfx-4v44-9qw9
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
