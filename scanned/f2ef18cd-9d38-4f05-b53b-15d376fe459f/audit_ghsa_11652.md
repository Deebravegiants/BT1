# [M] Rails Active Support has a possible DoS vulnerability in its number helpers

## Summary
Severity: Medium
Advisory: GHSA-2j26-frm8-cmj9
CVE: CVE-2026-33176
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-2j26-frm8-cmj9
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activesupport` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activesupport` — affected >=0 <7.2.3.1

## Details
### Impact
Active Support number helpers accept strings containing scientific notation (e.g. `1e10000`), which when converted to a string could be expanded into extremely large decimal representations. This can cause excessive memory allocation and CPU consumption when the expanded number is formatted, possibly resulting in a DoS vulnerability.

### Releases
The fixed releases are available at the normal locations.

### Credit
This issue was responsibly reported by Hackerone researcher [manun](https://hackerone.com/manun).

## References
- https://github.com/rails/rails/security/advisories/GHSA-2j26-frm8-cmj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33176
- https://github.com/rails/rails/commit/19dbab51ca086a657bb86458042bc44314916bcb
- https://github.com/rails/rails/commit/ebd6be18120d1136511eb516338e27af25ac0a1a
- https://github.com/rails/rails/commit/ee2c59e730e5b8faed502cd2c573109df093f856
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2026-33176.yml
