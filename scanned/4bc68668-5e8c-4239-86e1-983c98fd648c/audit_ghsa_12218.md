# [M] Cross site scripting that affects rails

## Summary
Severity: Medium
Advisory: GHSA-8qrh-h9m2-5fvf
CVE: CVE-2009-3009
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-8qrh-h9m2-5fvf
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=2.0.0 <2.2.3
- RubyGems: `actionpack` — affected >=2.3.0 <2.3.4
- RubyGems: `activesupport` — affected >=2.0.0 <2.2.3
- RubyGems: `activesupport` — affected >=2.3.0 <2.3.4

## Details
Cross-site scripting (XSS) vulnerability in Ruby on Rails 2.x before 2.2.3, and 2.3.x before 2.3.4, allows remote attackers to inject arbitrary web script or HTML by placing malformed Unicode strings into a form helper.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3009
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53036
- https://github.com/advisories/GHSA-8qrh-h9m2-5fvf
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2009-3009.yml
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=545063
- http://groups.google.com/group/rubyonrails-security/msg/7f57cd7794e1d1b4?dmode=source
- http://lists.apple.com/archives/security-announce/2010//Mar/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-10/msg00004.html
- http://secunia.com/advisories/36600
- http://secunia.com/advisories/36717
- http://securitytracker.com/id?1022824
- http://support.apple.com/kb/HT4077
- http://weblog.rubyonrails.org/2009/9/4/xss-vulnerability-in-ruby-on-rails
- http://www.debian.org/security/2009/dsa-1887
- http://www.osvdb.org/57666
- http://www.securityfocus.com/bid/36278
- http://www.vupen.com/english/advisories/2009/2544
