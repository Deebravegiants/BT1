# [H] Aimeos HTML client may potentially reveal sensitive information in error log

## Summary
Severity: High
Advisory: GHSA-ppm5-jv84-2xg2
CVE: CVE-2024-38516
CWE: CWE-1295
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-25
Source: https://github.com/advisories/GHSA-ppm5-jv84-2xg2
Type: github-advisory

## Affected
- Packagist: `aimeos/ai-client-html` — affected >=2024.04.1 <2024.04.7
- Packagist: `aimeos/ai-client-html` — affected >=2023.04.1 <2023.10.15
- Packagist: `aimeos/ai-client-html` — affected >=2022.04.1 <2022.10.13
- Packagist: `aimeos/ai-client-html` — affected >=2021.10.1 <2021.10.22

## Details
### Impact
Debug information can reveal sensitive information from environment variables in error log

### Affected platform
Laravel environments with multi-vendor setups and admin access for the vendors

## References
- https://github.com/aimeos/ai-client-html/security/advisories/GHSA-ppm5-jv84-2xg2
- https://nvd.nist.gov/vuln/detail/CVE-2024-38516
- https://github.com/aimeos/ai-client-html/commit/bb389620ffc3cf4a2f29c11a1e5f512049e0c132
- https://github.com/aimeos/ai-client-html
