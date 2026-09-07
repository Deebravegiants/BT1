# [C] Incorrect Permission Assignment for Critical Resource in ShopXO

## Summary
Severity: Critical
Advisory: GHSA-jfph-3hpg-2f65
CVE: CVE-2022-28056
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-jfph-3hpg-2f65
Type: github-advisory

## Affected
- Packagist: `shopxo/shopxo` — affected >=0 <2.2.6

## Details
ShopXO v2.2.5 and below was discovered to contain a system re-install vulnerability via the Add function in app/install/controller/Index.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28056
- https://github.com/gongfuxiang/shopxo/issues/66
- https://github.com/gongfuxiang/shopxo
