# [H] Spatie Browsershot Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-v528-6rq9-h6gw
CVE: CVE-2024-21547
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-v528-6rq9-h6gw
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <5.0.2

## Details
Versions of the package spatie/browsershot before 5.0.2 are vulnerable to Directory Traversal due to URI normalisation in the browser where the file:// check can be bypassed with file:\\. An attacker could read any file on the server by exploiting the normalization of \ into /.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21547
- https://github.com/spatie/browsershot/commit/dfc3635b83dd980e5c39f8f8c73e87723b99ca01
- https://gist.github.com/chuajianshen/baa71db588cfc038fb5d65624a47be81
- https://github.com/spatie/browsershot
- https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8501858
