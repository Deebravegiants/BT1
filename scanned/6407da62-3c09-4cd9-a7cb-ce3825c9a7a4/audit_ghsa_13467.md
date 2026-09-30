# [H] Decidim vulnerable to sensitive data disclosure

## Summary
Severity: High
Advisory: GHSA-jm79-9pm4-vrw9
CVE: CVE-2023-34090
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-jm79-9pm4-vrw9
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0.27.0 <0.27.3
- RubyGems: `decidim-meetings` — affected >=0.27.0 <0.27.3

## Details
Note: added the actual report as a [comment](https://github.com/decidim/decidim/security/advisories/GHSA-jm79-9pm4-vrw9#advisory-comment-81110).

### Summary

Decidim, a platform for digital citizen participation, uses a third-party library named Ransack for filtering certain database collections (e.g., public meetings). By default, this library allows filtering on all data attributes and associations. This allows an unauthenticated remote attacker to exfiltrate non-public data from the underlying database of a Decidim instance (e.g., exfiltrating data from the user table).

### Impact
This issue may lead to Sensitive Data Disclosure.

### Patches
The problem was patched in [v0.27.3](https://github.com/decidim/decidim/releases/tag/v0.27.3).

### Workarounds
Disable or unpublish all meetings components from your application.

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-jm79-9pm4-vrw9
- https://github.com/decidim/decidim/security/advisories/GHSA-jm79-9pm4-vrw9#advisory-comment-81110
- https://nvd.nist.gov/vuln/detail/CVE-2023-34090
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.27.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-meetings/CVE-2023-34090.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2023-34090.yml
