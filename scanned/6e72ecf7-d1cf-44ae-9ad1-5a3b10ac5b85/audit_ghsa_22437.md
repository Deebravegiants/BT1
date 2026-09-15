# [C] omniauth-weibo-oauth2 included a code-execution backdoor inserted by a third party

## Summary
Severity: Critical
Advisory: GHSA-vr22-43gj-rx3f
CVE: CVE-2019-17268
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vr22-43gj-rx3f
Type: github-advisory

## Affected
- RubyGems: `omniauth-weibo-oauth2` — affected >=0.4.6 <0.5.1

## Details
The omniauth-weibo-oauth2 gem 0.4.6 for Ruby, as distributed on RubyGems.org, included a code-execution backdoor inserted by a third party. Versions through 0.4.5, and 0.5.1 and later, are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17268
- https://github.com/beenhero/omniauth-weibo-oauth2/issues/36
- https://diff.coditsu.io/diffs/09a05c37-1b34-49e1-ac94-d4dda40d1ad1#d2h-971595
- https://github.com/beenhero/omniauth-weibo-oauth2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-weibo-oauth2/CVE-2019-17268.yml
