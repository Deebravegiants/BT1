# [M] actionpack Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-24fg-p96v-hxh8
CVE: CVE-2011-0447
CWE: CWE-352
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-24fg-p96v-hxh8
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=2.1.0 <2.3.11
- RubyGems: `actionpack` — affected >=3.0.0 <3.0.4

## Details
Ruby on Rails 2.1.x, 2.2.x, and 2.3.x before 2.3.11, and 3.x before 3.0.4, does not properly validate HTTP requests that contain an X-Requested-With header, which makes it easier for remote attackers to conduct cross-site request forgery (CSRF) attacks via forged (1) AJAX or (2) API requests that leverage "combinations of browser plugins and HTTP redirects," a related issue to CVE-2011-0696.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0447
- https://github.com/rails/rails/commit/66ce3843d32e9f2ac3b1da20067af53019bbb034
- https://github.com/rails/rails/commit/7e86f9b4d2b7dfa974c10ae7e6d8ef90f3d77f06
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2011-0447.yml
- https://web.archive.org/web/20120527023027/http://www.securityfocus.com/bid/46291
- https://web.archive.org/web/20170223045008/http://www.securitytracker.com/id?1025060
- http://groups.google.com/group/rubyonrails-security/msg/c22ea1668c0d181c?dmode=source&output=gplain
- http://lists.fedoraproject.org/pipermail/package-announce/2011-April/057650.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-March/055074.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-March/055088.html
- http://weblog.rubyonrails.org/2011/2/8/csrf-protection-bypass-in-ruby-on-rails
- http://www.debian.org/security/2011/dsa-2247
