# [M] Symfony vulnerable to Session Fixation of CSRF tokens

## Summary
Severity: Medium
Advisory: GHSA-3gv2-29qc-v67m
CVE: CVE-2022-24895
CWE: CWE-384, CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-3gv2-29qc-v67m
Type: github-advisory

## Affected
- Packagist: `symfony/security-bundle` — affected >=2.0.0 <4.4.50
- Packagist: `symfony/security-bundle` — affected >=5.0.0 <5.4.20
- Packagist: `symfony/security-bundle` — affected >=6.0.0 <6.0.20
- Packagist: `symfony/security-bundle` — affected >=6.1.0 <6.1.12
- Packagist: `symfony/security-bundle` — affected >=6.2.0 <6.2.6
- Packagist: `symfony/symfony` — affected >=2.0.0 <4.4.50
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.4.20
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.0.20
- Packagist: `symfony/symfony` — affected >=6.1.0 <6.1.12
- Packagist: `symfony/symfony` — affected >=6.2.0 <6.2.6

## Details
Description
-----------

When authenticating users Symfony by default regenerates the session ID upon login, but preserves the rest of session attributes. Because this does not clear CSRF tokens upon login, this might enables [same-site attackers](https://canitakeyoursubdomain.name/) to bypass the CSRF protection mechanism by performing an attack similar to a session-fixation.

Resolution
----------

Symfony removes all CSRF tokens from the session on successful login.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/5909d74ecee359ea4982fcf4331aaf2e489a1fd4) for branch 4.4.

Credits
-------

We would like to thank Marco Squarcina for reporting the issue and Nicolas Grekas for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-3gv2-29qc-v67m
- https://nvd.nist.gov/vuln/detail/CVE-2022-24895
- https://github.com/symfony/security-bundle/commit/076fd2088ada33d760758d98ff07ddedbf567946
- https://github.com/symfony/symfony/commit/5909d74ecee359ea4982fcf4331aaf2e489a1fd4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-bundle/CVE-2022-24895.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2022-24895.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2023/07/msg00014.html
- https://symfony.com/cve-2022-24895
