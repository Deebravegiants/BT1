# [H] Blind SQL Injection via GridFieldSortableHeader

## Summary
Severity: High
Advisory: GHSA-rr8h-f97q-8p9c
CVE: CVE-2022-38148
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-rr8h-f97q-8p9c
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.10.11
- Packagist: `silverstripe/framework` — affected >=4.11.0 <4.11.14

## Details
Gridfield state is vulnerable to SQL injections. The vast majority of Gridfields in Silverstripe CMS are affected by this vulnerability.

An attacker with CMS access could execute an arbitrary SQL statement by adding an SQL payload in some parts of the GridField state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38148
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-38148.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/CVE-2022-38148
