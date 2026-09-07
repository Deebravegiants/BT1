# [M] Wallabag user can delete own API client unintentionally

## Summary
Severity: Medium
Advisory: GHSA-gjvc-55fw-v6vq
CVE: CVE-2023-4455
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-gjvc-55fw-v6vq
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.0.0-alpha.1 <2.6.3

## Details
# Description
wallabag was discovered to contain a Cross-Site Request Forgery (CSRF) which allows attackers to arbitrarily delete API key via `/developer/client/delete/{id}` 

This vulnerability has a CVSSv3.1 score of 6.5.

**You should immediately patch your instance to version 2.6.3 or higher if you have more than one user and/or having open registration**.

# Resolution

This action is now doable only via POST method, which ensures that we can't do it via a 3rd-party website. 

# Credits 

We would like to thank @tht1997 for reporting this issue through huntr.dev.

Reference: https://huntr.dev/bounties/5ab1b206-5fe8-4737-b275-d705e76f193a/

## References
- https://github.com/wallabag/wallabag/security/advisories/GHSA-gjvc-55fw-v6vq
- https://github.com/wallabag/wallabag/commit/ffcc5c9062fcc8cd922d7d6d65edbe5efae96806
- https://github.com/wallabag/wallabag
- https://huntr.dev/bounties/5ab1b206-5fe8-4737-b275-d705e76f193a
