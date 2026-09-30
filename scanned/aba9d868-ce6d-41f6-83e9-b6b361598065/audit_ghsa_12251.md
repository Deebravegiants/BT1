# [M] Mail Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cpjc-p7fc-j9xh
CVE: CVE-2011-0739
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-cpjc-p7fc-j9xh
Type: github-advisory

## Affected
- RubyGems: `mail` — affected >=0 <2.2.15

## Details
The deliver function in the sendmail delivery agent (`lib/mail/network/delivery_methods/sendmail.rb`) in Ruby Mail gem 2.2.14 and earlier allows remote attackers to execute arbitrary commands via shell metacharacters in an e-mail address.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0739
- https://exchange.xforce.ibmcloud.com/vulnerabilities/65010
- https://github.com/mikel/mail
- https://github.com/mikel/mail/raw/master/patches/20110126_sendmail.patch
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mail/CVE-2011-0739.yml
- https://web.archive.org/web/20200228225346/http://www.securityfocus.com/bid/46021
- http://groups.google.com/group/mail-ruby/browse_thread/thread/e93bbd05706478dd?pli=1
