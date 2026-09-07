# [M] Wallabag user can disable 2FA unintentionally

## Summary
Severity: Medium
Advisory: GHSA-56fm-hfp3-x3w3
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-10-02
Source: https://github.com/advisories/GHSA-56fm-hfp3-x3w3
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.0.0-alpha.1 <2.6.7

## Details
## Impact
wallabag was discovered to contain a Cross-Site Request Forgery (CSRF) which allows attackers to arbitrarily disable 2FA through `/config/otp/app/disable` and `/config/otp/email/disable`.

This vulnerability has a CVSSv3.1 score of 4.3.

**You should upgrade your instance to version 2.6.7 or higher.**

## Resolution

These endpoints now require POST method.

## Credits

We would like to thank @dhina016 for reporting this issue through huntr.dev.

Reference: https://huntr.dev/bounties/4c446fe7-2a44-4907-b0cf-4ab77d75c487/

## References
- https://github.com/wallabag/wallabag/security/advisories/GHSA-56fm-hfp3-x3w3
- https://github.com/wallabag/wallabag/commit/0cfdddc2eb0aee5ffb69bf499d377d75655ba157
- https://github.com/wallabag/wallabag
- https://huntr.dev/bounties/4c446fe7-2a44-4907-b0cf-4ab77d75c487
