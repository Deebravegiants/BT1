# [M] Wallabag user can reset data unintentionally 

## Summary
Severity: Medium
Advisory: GHSA-p8gp-899c-jvq9
CVE: CVE-2023-4454
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-p8gp-899c-jvq9
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.0.0-alpha.1 <2.6.3

## Details
# Description

wallabag was discovered to contain a Cross-Site Request Forgery (CSRF) which allows attackers to arbitrarily reset annotations, entries and tags, by the GET request to `/reset/annotations`, `/reset/entries`, `/reset/tags`, `/reset/archived`.

This vulnerability has a CVSSv3.1 score of 4.3.

**You should immediately patch your instance to version 2.6.3 or higher if you have more than one user and/or having open registration**.

# Resolution

These actions are now doable only via POST method, which ensures that we can't do them via a 3rd-party website. 

# Credits 

We would like to thank @zpbrent for reporting this issue through huntr.dev.

Reference: https://huntr.dev/bounties/4ee0ef74-e4d4-46e7-a05c-076bce522299/

## References
- https://github.com/wallabag/wallabag/security/advisories/GHSA-p8gp-899c-jvq9
- https://github.com/wallabag/wallabag/commit/78b0b55c40511e1f22d5bbb4897aa10fca68441c
- https://github.com/wallabag/wallabag
- https://huntr.dev/bounties/4ee0ef74-e4d4-46e7-a05c-076bce522299
