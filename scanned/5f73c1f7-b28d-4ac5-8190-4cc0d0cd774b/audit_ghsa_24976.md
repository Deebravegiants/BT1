# [C] silverstripe restfulserver and registry modules SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4j6v-3895-8g2j
CVE: CVE-2019-12149
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4j6v-3895-8g2j
Type: github-advisory

## Affected
- Packagist: `silverstripe/restfulserver` — affected >=2.1.0 <2.1.2
- Packagist: `silverstripe/registry` — affected >=2.1.0 <2.1.1
- Packagist: `silverstripe/registry` — affected >=2.2.0 <2.2.1
- Packagist: `silverstripe/restfulserver` — affected >=1.0.0 <1.0.9
- Packagist: `silverstripe/restfulserver` — affected >=2.0.0 <2.0.4

## Details
SQL injection vulnerability in silverstripe/restfulserver module 1.0.x before 1.0.9, 2.0.x before 2.0.4, and 2.1.x before 2.1.2 and silverstripe/registry module 2.1.x before 2.1.1 and 2.2.x before 2.2.1 allows attackers to execute arbitrary SQL commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12149
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/restfulserver/CVE-2019-12149.yaml
- https://www.silverstripe.org/download/security-releases/cve-2019-12149
