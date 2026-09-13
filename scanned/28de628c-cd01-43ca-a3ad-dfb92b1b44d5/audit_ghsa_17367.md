# [H] alexusmai laravel-file-manager is vulnerable to Directory Traversal via the unzip/extraction functionality

## Summary
Severity: High
Advisory: GHSA-q5hg-wppq-r2cc
CVE: CVE-2025-65346
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-q5hg-wppq-r2cc
Type: github-advisory

## Affected
- Packagist: `alexusmai/laravel-file-manager` — affected >=0

## Details
alexusmai laravel-file-manager 3.3.1 and below is vulnerable to Directory Traversal. The unzip/extraction functionality improperly allows archive contents to be written to arbitrary locations on the filesystem due to insufficient validation of extraction paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65346
- https://github.com/Theethat-Thamwasin/CVE-2025-65346
- https://github.com/Theethat-Thamwasin/CVE-2025-65346/blob/main/POC-CVE-65346.md
- https://github.com/alexusmai/laravel-file-manager
