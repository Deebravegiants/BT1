# [H] SQL Injection in Pimcore

## Summary
Severity: High
Advisory: GHSA-mj2c-5mjv-gmmj
CVE: CVE-2022-1339
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-mj2c-5mjv-gmmj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.3.5

## Details
Pimcore prior to version 10.3.5 is vulnerable to SQL injection in ElementController.php. This vulnerability causes loss of data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1339
- https://github.com/pimcore/pimcore/commit/adae3be64427466bf0df15ceaea2ac30da93752c
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/ae8dc737-844e-40da-a9f7-e72d8e50f6f9
