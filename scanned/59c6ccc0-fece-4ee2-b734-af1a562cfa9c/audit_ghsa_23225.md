# [H] Incorrect Authorization in Dolibarr 

## Summary
Severity: High
Advisory: GHSA-rg8m-84jf-9367
CVE: CVE-2020-12669
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rg8m-84jf-9367
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <12.0.0

## Details
core/get_menudiv.php in Dolibarr before 11.0.4 allows remote authenticated attackers to bypass intended access restrictions via a non-alphanumeric menu parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12669
- https://github.com/Dolibarr/dolibarr/commit/c1b530f58f6f01081ddbeaa2092ef308c3ec2727
- https://github.com/Dolibarr/dolibarr
- https://sourceforge.net/projects/dolibarr/files/Dolibarr%20ERP-CRM/11.0.4
