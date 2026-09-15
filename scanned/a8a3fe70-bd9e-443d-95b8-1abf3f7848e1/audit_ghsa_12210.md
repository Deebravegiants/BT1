# [H] Thumbshooter vulnerable to Code Injection

## Summary
Severity: High
Advisory: GHSA-7fqj-cg79-f2pv
CVE: CVE-2013-1898
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-7fqj-cg79-f2pv
Type: github-advisory

## Affected
- RubyGems: `thumbshooter` — affected >=0

## Details
lib/thumbshooter.rb in the Thumbshooter 0.1.5 gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1898
- https://github.com/digineo/thumbshooter
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/thumbshooter/CVE-2013-1898.yml
- http://seclists.org/fulldisclosure/2013/Mar/218
- http://vapid.dhs.org/advisories/thumbshooter-ruby-gem-remoteexec.html
- http://www.openwall.com/lists/oss-security/2013/03/26/13
- http://www.openwall.com/lists/oss-security/2013/03/26/3
