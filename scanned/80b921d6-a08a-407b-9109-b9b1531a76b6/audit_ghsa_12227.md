# [M] activesupport vulnerable to Denial of Service via large XML document depth

## Summary
Severity: Medium
Advisory: GHSA-j96r-xvjq-r9pg
CVE: CVE-2015-3227
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-j96r-xvjq-r9pg
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=4.0.0.beta1 <4.1.11
- RubyGems: `activesupport` — affected >=4.2.0.beta1 <4.2.2
- RubyGems: `activesupport` — affected >=0 <3.2.22

## Details
The (1) `jdom.rb` and (2) `rexml.rb` components in Active Support in Ruby on Rails before 3.2.22, 4.1.x before 4.1.11, and 4.2.x before 4.2.2, when JDOM or REXML is enabled, allow remote attackers to cause a denial of service (SystemStackError) via a large XML document depth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3227
- https://github.com/rails/rails/commit/12f763ce1131d29d24bd0d8f868e2697a139aea3
- https://github.com/rails/rails/commit/153cc843ad95930b00b0ca91d30b599b7dec9680
- https://github.com/rails/rails/commit/78b29e08c700d889837af6c51c7debd3864abc3d
- https://github.com/rails/rails
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/bahr2JLnxvk/x4EocXnHPp8J
- https://web.archive.org/web/20200228041703/http://www.securityfocus.com/bid/75234
- https://web.archive.org/web/20200517005133/http://www.securitytracker.com/id/1033755
- http://lists.opensuse.org/opensuse-updates/2015-07/msg00050.html
- http://openwall.com/lists/oss-security/2015/06/16/16
- http://www.debian.org/security/2016/dsa-3464
