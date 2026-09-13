# [H] Improper validation in meraki

## Summary
Severity: High
Advisory: GHSA-6x4h-9622-fqr6
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-6x4h-9622-fqr6
Type: github-advisory

## Affected
- PyPI: `meraki` — affected >=0 <1.40.1

## Details
aiohttp is an asynchronous HTTP client/server framework for asyncio and Python. Improper validation made it possible for an attacker to modify the HTTP request (e.g. to insert a new header) or create a new HTTP request if the attacker controls the HTTP version. The vulnerability only occurs if the attacker can control the HTTP version of the request. This issue has been patched in version 3.9.0.

meraki from version 1.40.1 requires aiohttp 3.9.0

## References
- https://github.com/meraki/dashboard-api-python/security/advisories/GHSA-6x4h-9622-fqr6
- https://nvd.nist.gov/vuln/detail/CVE-2023-49081
- https://github.com/meraki/dashboard-api-python
- https://github.com/meraki/dashboard-api-python/releases/tag/1.40.1
