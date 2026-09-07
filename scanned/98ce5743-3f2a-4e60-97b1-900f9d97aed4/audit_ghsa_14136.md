# [H] Dolibarr vulnerable to remote code execution via uppercase manipulation

## Summary
Severity: High
Advisory: GHSA-9wqr-5jp4-mjmh
CVE: CVE-2023-30253
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-29
Source: https://github.com/advisories/GHSA-9wqr-5jp4-mjmh
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <17.0.1

## Details
Dolibarr before 17.0.1 allows remote code execution by an authenticated user via an uppercase manipulation: <?PHP instead of <?php in injected data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30253
- https://github.com/Dolibarr/dolibarr
- https://www.swascan.com/blog
- https://www.swascan.com/security-advisory-dolibarr-17-0-0
