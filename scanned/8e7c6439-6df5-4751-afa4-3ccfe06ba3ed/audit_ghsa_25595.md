# [H] SQL Injection in Pimcore

## Summary
Severity: High
Advisory: GHSA-6gm7-j668-w6h9
CVE: CVE-2022-1219
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-09
Source: https://github.com/advisories/GHSA-6gm7-j668-w6h9
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.3.5

## Details
Pimcore prior to version 10.3.5 is vulnerable SQL injection in RecyclebinController.php. This vulnerability affects data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1219
- https://github.com/pimcore/pimcore/commit/a697830359df06246acca502ee2455614de68017
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/f700bd18-1fd3-4a05-867f-07176aebc7f6
