# [M] actionpack Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-92w9-2pqw-rhjj
CVE: CVE-2012-3424
CWE: CWE-287
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-92w9-2pqw-rhjj
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0.beta <3.0.16
- RubyGems: `actionpack` — affected >=3.1.0 <3.1.7
- RubyGems: `actionpack` — affected >=3.2.0 <3.2.7
- RubyGems: `actionpack` — affected >=0 <2.3.5

## Details
The `decode_credentials` method in `actionpack/lib/action_controller/metal/http_authentication.rb` in Ruby on Rails before 3.0.16, 3.1.x before 3.1.7, and 3.2.x before 3.2.7 converts Digest Authentication strings to symbols, which allows remote attackers to cause a denial of service by leveraging access to an application that uses a `with_http_digest` helper method, as demonstrated by the `authenticate_or_request_with_http_digest` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3424
- https://github.com/rails/rails/commit/3719bd3e95523c5518507dbe44f260f252930600
- https://github.com/rails/rails
- https://groups.google.com/group/rubyonrails-security/msg/244d32f2fa25147d?hl=en&dmode=source&output=gplain
- http://lists.opensuse.org/opensuse-updates/2012-08/msg00046.html
- http://rhn.redhat.com/errata/RHSA-2013-0154.html
- http://weblog.rubyonrails.org/2012/7/26/ann-rails-3-2-7-has-been-released
