# [H] Browsershot Server-Side Request Forgery (SSRF) via setURL() Function

## Summary
Severity: High
Advisory: GHSA-qw64-6vcc-8ghx
CVE: CVE-2025-3192
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-qw64-6vcc-8ghx
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0

## Details
Versions of the package spatie/browsershot from 0.0.0 to 5.0.3 are vulnerable to Server-side Request Forgery (SSRF) in the setUrl() function due to a missing restriction on user input, enabling attackers to access localhost and list all of its directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3192
- https://gist.github.com/JunMing27/651998a34d57fbf71ff9d25386f1da0f
- https://github.com/spatie/browsershot
- https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8548015
