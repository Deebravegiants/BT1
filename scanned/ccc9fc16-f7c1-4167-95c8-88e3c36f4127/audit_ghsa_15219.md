# [M] Cross-site scripting (XSS) in Action messages on Avo

## Summary
Severity: Medium
Advisory: GHSA-g8vp-2v5p-9qfh
CVE: CVE-2024-22411
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-17
Source: https://github.com/advisories/GHSA-g8vp-2v5p-9qfh
Type: github-advisory

## Affected
- RubyGems: `avo` — affected >=3.0.0.beta1 <3.3.0
- RubyGems: `avo` — affected >=0 <2.47.0

## Details
Avo is a framework to create admin panels for Ruby on Rails apps. In Avo 3 pre12, any HTML inside text that is passed to `error` or `succeed` in an `Avo::BaseAction` subclass will be rendered directly without sanitization in the toast/notification that appears in the UI on Action completion. A malicious user could exploit this vulnerability to trigger a cross site scripting attack on an unsuspecting user. This issue has been addressed in the 3.3.0 and 2.47.0 releases of Avo. Users are advised to upgrade.

## References
- https://github.com/avo-hq/avo/security/advisories/GHSA-g8vp-2v5p-9qfh
- https://nvd.nist.gov/vuln/detail/CVE-2024-22411
- https://github.com/avo-hq/avo/commit/51bb80b181cd8e31744bdc4e7f9b501c81172347
- https://github.com/avo-hq/avo/commit/fc92a05a8556b1787c8694643286a1afa6a71258
- https://github.com/avo-hq/avo
- https://github.com/avo-hq/avo/releases/tag/v2.47.0
- https://github.com/avo-hq/avo/releases/tag/v3.3.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/avo/CVE-2024-22411.yml
