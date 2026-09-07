# [M] Moderate severity vulnerability that affects rails

## Summary
Severity: Medium
Advisory: GHSA-9p3v-wf2w-v29c
CVE: CVE-2009-4214
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9p3v-wf2w-v29c
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=0 <2.2.2
- RubyGems: `rails` — affected >=2.3.0 <2.3.5

## Details
Cross-site scripting (XSS) vulnerability in the strip_tags function in Ruby on Rails before 2.2.s, and 2.3.x before 2.3.5, allows remote attackers to inject arbitrary web script or HTML via vectors involving non-printing ASCII characters, related to HTML::Tokenizer and actionpack/lib/action_controller/vendor/html-scanner/html/node.rb.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4214
- https://github.com/advisories/GHSA-9p3v-wf2w-v29c
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2009-4214.yml
- http://github.com/rails/rails
- http://github.com/rails/rails/commit/bfe032858077bb2946abe25e95e485ba6da86bd5
- http://groups.google.com/group/rubyonrails-security/browse_thread/thread/4d4f71f2aef4c0ab?pli=1
- http://lists.apple.com/archives/security-announce/2010//Mar/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2010-03/msg00004.html
- http://secunia.com/advisories/37446
- http://secunia.com/advisories/38915
- http://support.apple.com/kb/HT4077
- http://weblog.rubyonrails.org/2009/11/30/ruby-on-rails-2-3-5-released
- http://www.debian.org/security/2011/dsa-2260
- http://www.debian.org/security/2011/dsa-2301
- http://www.openwall.com/lists/oss-security/2009/11/27/2
- http://www.openwall.com/lists/oss-security/2009/12/08/3
- http://www.securityfocus.com/bid/37142
- http://www.securitytracker.com/id?1023245
- http://www.vupen.com/english/advisories/2009/3352
