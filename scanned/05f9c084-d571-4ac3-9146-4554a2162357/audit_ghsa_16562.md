# [H] silverstripe/taxonomy SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p2v5-xcqm-4fv6
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-p2v5-xcqm-4fv6
Type: github-advisory

## Affected
- Packagist: `silverstripe/taxonomy` — affected >=1.3.0 <1.3.1
- Packagist: `silverstripe/taxonomy` — affected >=2.0.0 <2.0.1

## Details
There is a vulnerability in silverstripe/taxonomy module that allows SQL injection. This affected controller (`TaxonomyDirectoryController`) is disabled by default and must be enabled by a developer for the exploit to be possible.

## References
- https://github.com/silverstripe/silverstripe-taxonomy/commit/01a5d9e04b993df507058aa53e6e18efc5ca405b
- https://github.com/silverstripe/silverstripe-taxonomy/commit/d037941e931490c33af5029c676447ed38896ee8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/taxonomy/SS-2018-011-1.yaml
- https://github.com/silverstripe/silverstripe-taxonomy
- https://www.silverstripe.org/download/security-releases/ss-2018-011
