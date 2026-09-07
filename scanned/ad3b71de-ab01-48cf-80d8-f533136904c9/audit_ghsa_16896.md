# [C] Drupal Core Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-297x-j9pm-xjgg
CVE: CVE-2018-7602
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-297x-j9pm-xjgg
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.59
- Packagist: `drupal/core` — affected >=8.0 <8.4.8
- Packagist: `drupal/core` — affected >=8.5 <8.5.3
- Packagist: `drupal/drupal` — affected >=7.0 <7.59
- Packagist: `drupal/drupal` — affected >=8.0 <8.4.8
- Packagist: `drupal/drupal` — affected >=8.5 <8.5.3

## Details
A remote code execution vulnerability exists within multiple subsystems of Drupal 7.x and 8.x. This potentially allows attackers to exploit multiple attack vectors on a Drupal site, which could result in the site being compromised. This vulnerability is related to Drupal core - Highly critical - Remote Code Execution - SA-CORE-2018-002. Both SA-CORE-2018-002 and this vulnerability are being exploited in the wild.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7602
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2018-7602.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2018-7602.yaml
- https://github.com/drupal/core
- https://lists.debian.org/debian-lts-announce/2018/04/msg00030.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-7602
- https://www.debian.org/security/2018/dsa-4180
- https://www.drupal.org/sa-core-2018-004
- https://www.exploit-db.com/exploits/44542
- https://www.exploit-db.com/exploits/44557
