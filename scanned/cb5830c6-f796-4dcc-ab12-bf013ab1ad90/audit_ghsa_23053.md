# [M] Sup Code Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5f2p-6vjv-2q2m
CVE: CVE-2013-4478
CWE: CWE-94
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5f2p-6vjv-2q2m
Type: github-advisory

## Affected
- RubyGems: `sup` — affected >=0 <0.13.2.1
- RubyGems: `sup` — affected >=0.14.0 <0.14.1.1

## Details
Sup before 0.13.2.1 and 0.14.x before 0.14.1.1 allows remote attackers to execute arbitrary commands via shell metacharacters in the filename of an email attachment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4478
- https://github.com/sup-heliotrope/sup/commit/8b46cdbfc14e07ca07d403aa28b0e7bc1c544785
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sup/CVE-2013-4478.yml
- https://github.com/sup-heliotrope/sup
- https://web.archive.org/web/20140524005344/http://rubyforge.org/pipermail/sup-talk/2013-October/004996.html
- https://web.archive.org/web/20140524012714/http://rubyforge.org/pipermail/sup-talk/2013-August/004993.html
- http://rubyforge.org/pipermail/sup-talk/2013-August/004993.html
- http://rubyforge.org/pipermail/sup-talk/2013-October/004996.html
- http://www.debian.org/security/2012/dsa-2805
- http://www.openwall.com/lists/oss-security/2013/10/30/2
- http://www.phenoelit.org/stuff/whatsup.txt
