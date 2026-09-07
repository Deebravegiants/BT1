# [M] Rembg allows SSRF via /api/remove

## Summary
Severity: Medium
Advisory: GHSA-r5gx-c49x-h878
CVE: CVE-2025-25301
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-r5gx-c49x-h878
Type: github-advisory

## Affected
- PyPI: `rembg` — affected >=0

## Details
Rembg is a tool to remove images background. In Rembg 2.0.57 and earlier, the /api/remove endpoint takes a URL query parameter that allows an image to be fetched, processed and returned. An attacker may be able to query this endpoint to view pictures hosted on the internal network of the rembg server. This issue may lead to Information Disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25301
- https://github.com/danielgatis/rembg
- https://securitylab.github.com/advisories/GHSL-2024-161_GHSL-2024-162_rembg
