# [M] MoonShine Arbitrary File Upload Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8xfq-7f6m-mpmf
CVE: CVE-2025-51489
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-8xfq-7f6m-mpmf
Type: github-advisory

## Affected
- Packagist: `moonshine/moonshine` — affected >=0 <3.12.5

## Details
An arbitrary file upload vulnerability in MoonShine v3.12.4 allows attackers to execute arbitrary code via uploading a crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51489
- https://github.com/moonshine-software/moonshine/commit/7102fb113627870fb1cb7176e1d0d95bb47a7fd4
- https://github.com/GiacoLenzo2109/MoonShine_Software_PoCs
- https://github.com/moonshine-software/moonshine
