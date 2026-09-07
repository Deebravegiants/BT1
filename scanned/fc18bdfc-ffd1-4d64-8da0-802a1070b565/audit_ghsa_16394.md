# [H] Bagisto Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-7p7q-fjfw-v3gf
CVE: CVE-2023-36237
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-7p7q-fjfw-v3gf
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <1.3.2

## Details
Cross Site Request Forgery vulnerability in Bagisto before v.1.3.2 allows an attacker to execute arbitrary code via a crafted HTML script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36237
- https://github.com/bagisto/bagisto/commit/265aa14db1490005fa4e0d6fe714835abb689813
- https://github.com/Ek-Saini/security/blob/main/CSRF-Bagisto
- https://github.com/bagisto/bagisto
- https://github.com/bagisto/bagisto/commits/v1.3.2/?after=2dbb988388bc480af4bc8e880caed500772cfbc7+139
