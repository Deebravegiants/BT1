# [H] laravel-admin has Arbitrary File Upload vulnerability

## Summary
Severity: High
Advisory: GHSA-g857-47pm-3r32
CVE: CVE-2023-24249
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-27
Source: https://github.com/advisories/GHSA-g857-47pm-3r32
Type: github-advisory

## Affected
- Packagist: `encore/laravel-admin` — affected >=0

## Details
An arbitrary file upload vulnerability in laravel-admin v1.8.19 allows attackers to execute arbitrary code via a crafted PHP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24249
- https://github.com/z-song/laravel-admin/issues/5726
- https://flyd.uk/post/cve-2023-24249
- https://github.com/z-song/laravel-admin
- https://laravel-admin.org
