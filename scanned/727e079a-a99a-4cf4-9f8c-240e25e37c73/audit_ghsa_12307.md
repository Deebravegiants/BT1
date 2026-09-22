# [H] Ruby on Rails vulnerable to code injection

## Summary
Severity: High
Advisory: GHSA-rvpq-5xqx-pfpp
CVE: CVE-2006-4111
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-rvpq-5xqx-pfpp
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=1.1.0 <1.1.6

## Details
Ruby on Rails before 1.1.5 allows remote attackers to execute Ruby code with "severe" or "serious" impact via a File Upload request with an HTTP header that modifies the LOAD_PATH variable, a different vulnerability than CVE-2006-4112.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-4111
- https://github.com/presidentbeef/rails-security-history/blob/master/vulnerabilities.md
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2006-4111.yml
- https://web.archive.org/web/20200301174340/http://www.securityfocus.com/bid/19454
- https://web.archive.org/web/20200808083046/http://securitytracker.com/id?1016673
- http://blog.koehntopp.de/archives/1367-Ruby-On-Rails-Mandatory-Mystery-Patch.html
- http://weblog.rubyonrails.org/2006/8/9/rails-1-1-5-mandatory-security-patch-and-other-tidbits
- http://www.gentoo.org/security/en/glsa/glsa-200608-20.xml
- http://www.novell.com/linux/security/advisories/2006_21_sr.html
