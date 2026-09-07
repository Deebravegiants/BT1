# [H] XSS/Script injection vulnerability in matestack

## Summary
Severity: High
Advisory: GHSA-3jqw-vv45-mjhh
CVE: CVE-2020-5241
CWE: CWE-80
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-02-12
Source: https://github.com/advisories/GHSA-3jqw-vv45-mjhh
Type: github-advisory

## Affected
- RubyGems: `matestack-ui-core` — affected >=0 <0.7.4

## Details
matestack-ui-core (RubyGem) before 0.7.4 is vulnerable to XSS/Script injection.

This vulnerability is patched in version 0.7.4.

## References
- https://github.com/matestack/matestack-ui-core/security/advisories/GHSA-3jqw-vv45-mjhh
- https://nvd.nist.gov/vuln/detail/CVE-2020-5241
- https://github.com/matestack/matestack-ui-core/commit/5c61571739e860db9ca578fe09ab4733878cb0fc
- https://github.com/matestack/matestack-ui-core/commit/e96915cf20c4fa0571df7fa21e9b09a69be19107
- https://github.com/matestack/matestack-ui-core
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/matestack-ui-core/CVE-2020-5241.yml
