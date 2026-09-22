# [H] Command injection in czproject/git-php

## Summary
Severity: High
Advisory: GHSA-3xpw-vhmv-cw7h
CVE: CVE-2022-25866
CWE: CWE-74, CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-3xpw-vhmv-cw7h
Type: github-advisory

## Affected
- Packagist: `czproject/git-php` — affected >=0 <4.0.3

## Details
The package czproject/git-php before 4.0.3 are vulnerable to Command Injection via git argument injection. When calling the isRemoteUrlReadable($url, array $refs = NULL) function, both the url and refs parameters are passed to the git ls-remote subcommand in a way that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25866
- https://github.com/czproject/git-php/commit/5e82d5479da5f16d37a915de4ec55e1ac78de733
- https://github.com/czproject/git-php
- https://github.com/czproject/git-php/releases/tag/v4.0.3
- https://snyk.io/vuln/SNYK-PHP-CZPROJECTGITPHP-2421349
