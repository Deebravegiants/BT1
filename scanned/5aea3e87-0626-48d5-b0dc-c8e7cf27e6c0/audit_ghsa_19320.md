# [M] JRuby-OpenSSL has hostname verification disabled by default

## Summary
Severity: Medium
Advisory: GHSA-72qj-48g4-5xgx
CVE: CVE-2025-46551
CWE: CWE-295, CWE-297
Ecosystem: Maven, RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-72qj-48g4-5xgx
Type: github-advisory

## Affected
- Maven: `rubygems:jruby-openssl` — affected >=0.12.1 <0.15.4
- Maven: `org.jruby:jruby` — affected >=10.0.0.0 <10.0.0.1
- Maven: `org.jruby:jruby` — affected >=9.3.4.0 <9.4.12.1
- RubyGems: `jruby-openssl` — affected >=0.12.1 <0.15.4

## Details
### Summary
When verifying SSL certificates, jruby-openssl is not verifying that the hostname presented in the certificate matches the one we are trying to connect to, meaning a MITM could just present _any_ valid cert for a completely different domain they own, and JRuby wouldn't complain. 

### Details
n/a

### PoC
An example domain bad.substitutealert.com was created to present the a certificate for the domain s8a.me. The following script run in IRB in CRuby 3.4.3 will fail with `certificate verify failed (hostname mismatch)`, but will work just fine in JRuby 10.0.0.0 and JRuby 9.4.2.0, both of which use jruby-openssl version 0.15.3

```ruby
require "net/http"
require "openssl"

uri   = URI("https://bad.substitutealert.com/")
https = Net::HTTP.new(uri.host, uri.port)
https.use_ssl      = true
https.verify_mode  = OpenSSL::SSL::VERIFY_PEER

body = https.start { https.get(uri.request_uri).body }
puts body
```

### Impact
Anybody using JRuby to make requests of external APIs, or scraping the web, that depends on https to connect securely

## References
- https://github.com/jruby/jruby-openssl/security/advisories/GHSA-72qj-48g4-5xgx
- https://nvd.nist.gov/vuln/detail/CVE-2025-46551
- https://github.com/jruby/jruby-openssl/commit/31a56d690ce9b8af47af09aaaf809081949ed285
- https://github.com/jruby/jruby-openssl/commit/b1fc5d645c0d90891b8865925ac1c15e3f15a055
- https://github.com/jruby/jruby-openssl
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jruby-openssl/CVE-2025-46551.yml
