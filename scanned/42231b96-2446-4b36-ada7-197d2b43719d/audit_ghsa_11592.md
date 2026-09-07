# [M] Trix has a Stored XSS vulnerability through serialized attributes

## Summary
Severity: Medium
Advisory: GHSA-qmpg-8xg6-ph5q
CVE: CVE-2026-73426
CWE: CWE-79
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-qmpg-8xg6-ph5q
Type: github-advisory

## Affected
- RubyGems: `action_text-trix` — affected >=0 <2.1.17
- npm: `trix` — affected >=0 <2.1.17

## Details
### Impact
The Trix editor, in versions prior to 2.1.17, is vulnerable to XSS attacks when a `data-trix-serialized-attributes` attribute bypasses the DOMPurify sanitizer.

An attacker could craft HTML containing a `data-trix-serialized-attributes` attribute with a malicious payload that, when the content is rendered, could execute arbitrary JavaScript code within the context of the user's session, potentially leading to unauthorized actions being performed or sensitive information being disclosed.

### Patches
Update Recommendation: Users should upgrade to Trix editor version 2.1.17 or later.

### References
The XSS vulnerability was responsibly reported by Hackerone researcher [newbiefromcoma](https://hackerone.com/newbiefromcoma).

## References
- https://github.com/basecamp/trix/security/advisories/GHSA-qmpg-8xg6-ph5q
- https://github.com/basecamp/trix/pull/1282
- https://github.com/basecamp/trix/commit/53197ab5a142e6b0b76127cb790726b274eaf1bc
- https://github.com/basecamp/trix
- https://github.com/basecamp/trix/releases/tag/v2.1.17
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/action_text-trix/GHSA-qmpg-8xg6-ph5q.yml
