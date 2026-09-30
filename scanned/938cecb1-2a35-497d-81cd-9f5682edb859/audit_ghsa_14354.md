# [H] Arbitrary file read via SQL injection

## Summary
Severity: High
Advisory: GHSA-8r4m-5p6p-52rp
CVE: CVE-2023-30545
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-8r4m-5p6p-52rp
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.0.0 <8.0.4
- Packagist: `prestashop/prestashop` — affected >=0 <1.7.8.9

## Details
### Impact
It is possible for a user having access to the SQL Manager (Advanced Options -> Database) to arbitrary read any file on the Operating system when using SQL function LOAD_FILE in a SELECT request. So It can access to critical information.

### Patches
The patch will be on PS 8.0.4 and PS 1.7.8.9

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-8r4m-5p6p-52rp
- https://nvd.nist.gov/vuln/detail/CVE-2023-30545
- https://github.com/PrestaShop/PrestaShop/commit/cddac4198a47c602878a787280d813f60c6c0630
- https://github.com/PrestaShop/PrestaShop/commit/d900806e1841a31f26ff0a1843a6888fc1bb7f81
- https://github.com/PrestaShop/PrestaShop
