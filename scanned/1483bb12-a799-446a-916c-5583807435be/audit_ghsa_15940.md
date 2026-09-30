# [H] Starlette Denial of service (DoS) via multipart/form-data

## Summary
Severity: High
Advisory: GHSA-f96h-pmfr-66vw
CVE: CVE-2024-47874
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-f96h-pmfr-66vw
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <0.40.0

## Details
### Summary
Starlette treats `multipart/form-data` parts without a `filename` as text form fields and buffers those in byte strings with no size limit. This allows an attacker to upload arbitrary large form fields and cause Starlette to both slow down significantly due to excessive memory allocations and copy operations, and also consume more and more memory until the server starts swapping and grinds to a halt, or the OS terminates the server process with an OOM error. Uploading multiple such requests in parallel may be enough to render a service practically unusable, even if reasonable request size limits are enforced by a reverse proxy in front of Starlette.

### PoC

```python
from starlette.applications import Starlette
from starlette.routing import Route

async def poc(request):
    async with request.form():
        pass

app = Starlette(routes=[
    Route('/', poc, methods=["POST"]),
])
```

```sh
curl http://localhost:8000 -F 'big=</dev/urandom'
```

### Impact
This Denial of service (DoS) vulnerability affects all applications built with Starlette (or FastAPI) accepting form requests.

## References
- https://github.com/encode/starlette/security/advisories/GHSA-f96h-pmfr-66vw
- https://nvd.nist.gov/vuln/detail/CVE-2024-47874
- https://github.com/encode/starlette/commit/fd038f3070c302bff17ef7d173dbb0b007617733
- https://github.com/encode/starlette
