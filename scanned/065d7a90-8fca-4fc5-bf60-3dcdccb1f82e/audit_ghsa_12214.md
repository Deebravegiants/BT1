# [M] Web Console (Ruby gem) contains whitelisted_ips bypass

## Summary
Severity: Medium
Advisory: GHSA-67j6-xv27-w6ww
CVE: CVE-2015-3224
CWE: CWE-284
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-67j6-xv27-w6ww
Type: github-advisory

## Affected
- RubyGems: `web-console` — affected >=0 <2.1.3

## Details
request.rb in Web Console before 2.1.3, as used with Ruby on Rails 3.x and 4.x, does not properly restrict the use of X-Forwarded-For headers in determining a client's IP address, which allows remote attackers to bypass the whitelisted_ips protection mechanism via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3224
- https://github.com/rails/web-console
- https://github.com/rails/web-console/blob/master/CHANGELOG.markdown
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/web-console/CVE-2015-3224.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/lzmz9_ijUFw
- http://lists.fedoraproject.org/pipermail/package-announce/2015-June/160881.html
- http://openwall.com/lists/oss-security/2015/06/16/18
