# [H] Mustache remote code injection vulnerability

## Summary
Severity: High
Advisory: GHSA-4rmr-c2jx-vx27
CVE: CVE-2022-0323
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-4rmr-c2jx-vx27
Type: github-advisory

## Affected
- Packagist: `mustache/mustache` — affected >=2.0.0 <2.14.1

## Details
In Mustache.php v2.0.0 through v2.14.0, Sections tag can lead to arbitrary php code execution even if strict_callables is true when section value is controllable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0323
- https://github.com/bobthecow/mustache.php/commit/579ffa5c96e1d292c060b3dd62811ff01ad8c24e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mustache/mustache/CVE-2022-0323.yaml
- https://github.com/bobthecow/mustache.php
- https://github.com/bobthecow/mustache.php/releases/tag/v2.14.1
- https://huntr.dev/bounties/a5f5a988-aa52-4443-839d-299a63f44fb7
