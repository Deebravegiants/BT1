# [M] Statamic CMS vulnerable to email enumeration via forgot password endpoint

## Summary
Severity: Medium
Advisory: GHSA-m24v-f7g5-gq67
CVE: CVE-2026-44306
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-m24v-f7g5-gq67
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.21
- Packagist: `statamic/cms` — affected >=6.0.0 <6.15.0

## Details
### Impact

Responses from the forgot password forms hinted at whether an account existed for a given email address. An unauthenticated attacker could use this to enumerate valid users, which can aid in follow-up credential-based attacks.

### Patches

This has been fixed in 5.73.21 and 6.15.0. The forgot password forms now return the same generic response regardless of whether the submitted email matches a registered user.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-m24v-f7g5-gq67
- https://nvd.nist.gov/vuln/detail/CVE-2026-44306
- https://github.com/statamic/cms
