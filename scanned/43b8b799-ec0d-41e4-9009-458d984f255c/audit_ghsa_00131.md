# [H] Jekyll allows attackers to access arbitrary files by specifying a symlink

## Summary
Severity: High
Advisory: GHSA-4xjh-m3qx-49wc
CVE: CVE-2018-17567
CWE: CWE-59
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-09-28
Source: https://github.com/advisories/GHSA-4xjh-m3qx-49wc
Type: github-advisory

## Affected
- RubyGems: `jekyll` — affected >=0 <3.6.3
- RubyGems: `jekyll` — affected >=3.7.0 <3.7.4
- RubyGems: `jekyll` — affected >=3.8.0 <3.8.4

## Details
Jekyll through 3.6.2, 3.7.x through 3.7.3, and 3.8.x through 3.8.3 allows attackers to access arbitrary files by specifying a symlink in the `include` key in the `_config.yml` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17567
- https://github.com/jekyll/jekyll/pull/7224
- https://github.com/jekyll/jekyll
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jekyll/CVE-2018-17567.yml
- https://jekyllrb.com/news/2018/09/19/security-fixes-for-3-6-3-7-3-8
- https://lists.apache.org/thread.html/71da391f584b2fb301d2df0e491b279d87287e2fb4b11309f04ad984@%3Ccommits.accumulo.apache.org%3E
