# [M] jquery-rails and jquery-ujs subject to Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-4whc-pp4x-9pf3
CVE: CVE-2015-1840
CWE: CWE-200
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-4whc-pp4x-9pf3
Type: github-advisory

## Affected
- RubyGems: `jquery-rails` — affected >=0 <3.1.3
- RubyGems: `jquery-rails` — affected >=4.0.0 <4.0.4
- RubyGems: `jquery-ujs` — affected >=0 <1.0.4

## Details
jquery_ujs.js in jquery-rails before 3.1.3 and 4.x before 4.0.4 and rails.js in jquery-ujs before 1.0.4, as used with Ruby on Rails 3.x and 4.x, allow remote attackers to bypass the Same Origin Policy, and trigger transmission of a CSRF token to a different-domain web server, via a leading space character in a URL within an attribute value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1840
- https://github.com/advisories/GHSA-4whc-pp4x-9pf3
- https://github.com/rails/jquery-rails
- https://github.com/rails/jquery-rails/blob/master/CHANGELOG.md
- https://github.com/rails/jquery-ujs/blob/master/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jquery-rails/CVE-2015-1840.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jquery-ujs/CVE-2015-1840.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/XIZPbobuwaY
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/XIZPbobuwaY/fqnzzpuOlA4J
- https://web.archive.org/web/20200228084945/http://www.securityfocus.com/bid/75239
- http://lists.fedoraproject.org/pipermail/package-announce/2015-June/160906.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-June/161043.html
- http://lists.opensuse.org/opensuse-updates/2015-07/msg00041.html
- http://openwall.com/lists/oss-security/2015/06/16/15
