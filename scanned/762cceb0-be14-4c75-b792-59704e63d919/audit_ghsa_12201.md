# [H] Rails Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-9wrq-xvmp-xjc8
CVE: CVE-2006-4112
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9wrq-xvmp-xjc8
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=1.1.0 <1.1.6

## Details
Unspecified vulnerability in the "dependency resolution mechanism" in Ruby on Rails 1.1.0 through 1.1.5 allows remote attackers to execute arbitrary Ruby code via a URL that is not properly handled in the routing code, which leads to a denial of service (application hang) or "data loss," a different vulnerability than CVE-2006-4111.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-4112
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28364
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2006-4112.yml
- https://web.archive.org/web/20200301174340/http://www.securityfocus.com/bid/19454
- https://web.archive.org/web/20200804225700/http://www.securityfocus.com/archive/1/442934/100/0/threaded
- https://web.archive.org/web/20200808083046/http://securitytracker.com/id?1016673
- http://weblog.rubyonrails.org/2006/8/10/rails-1-1-6-backports-and-full-disclosure
- http://www.gentoo.org/security/en/glsa/glsa-200608-20.xml
- http://www.kb.cert.org/vuls/id/699540
- http://www.novell.com/linux/security/advisories/2006_21_sr.html
