# [M] aiohttp allows request smuggling due to incorrect parsing of chunk extensions

## Summary
Severity: Medium
Advisory: GHSA-8495-4g3g-x7pr
CVE: CVE-2024-52304
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-8495-4g3g-x7pr
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.10.11

## Details
### Summary
The Python parser parses newlines in chunk extensions incorrectly which can lead to request smuggling vulnerabilities under certain conditions.

### Impact
If a pure Python version of aiohttp is installed (i.e. without the usual C extensions) or `AIOHTTP_NO_EXTENSIONS` is enabled, then an attacker may be able to execute a request smuggling attack to bypass certain firewalls or proxy protections.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/259edc369075de63e6f3a4eaade058c62af0df71

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-8495-4g3g-x7pr
- https://nvd.nist.gov/vuln/detail/CVE-2024-52304
- https://github.com/aio-libs/aiohttp/commit/259edc369075de63e6f3a4eaade058c62af0df71
- https://github.com/aio-libs/aiohttp
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
