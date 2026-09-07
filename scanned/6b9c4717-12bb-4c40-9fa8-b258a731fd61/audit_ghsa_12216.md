# [C] rails vulnerable to improper authentication

## Summary
Severity: Critical
Advisory: GHSA-rxq3-gm4p-5fj4
CVE: CVE-2009-2422
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-rxq3-gm4p-5fj4
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=0 <2.3.3

## Details
The example code for the digest authentication functionality (http_authentication.rb) in Ruby on Rails before 2.3.3 defines an authenticate_or_request_with_http_digest block that returns nil instead of false when the user does not exist, which allows context-dependent attackers to bypass authentication for applications that are derived from this example by sending an invalid username without a password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2422
- https://exchange.xforce.ibmcloud.com/vulnerabilities/51528
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2009-2422.yml
- https://web.archive.org/web/20090711160153/http://secunia.com/advisories/35702
- https://web.archive.org/web/20200229192617/http://www.securityfocus.com/bid/35579
- http://lists.apple.com/archives/security-announce/2010//Mar/msg00001.html
- http://n8.tumblr.com/post/117477059/security-hole-found-in-rails-2-3s
- http://support.apple.com/kb/HT4077
- http://weblog.rubyonrails.org/2009/6/3/security-problem-with-authenticate_with_http_digest
