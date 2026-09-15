# [H] lawn-login exposes database password to unauthorized users

## Summary
Severity: High
Advisory: GHSA-rhgq-vv9x-j4p5
CVE: CVE-2014-5000
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-01-22
Source: https://github.com/advisories/GHSA-rhgq-vv9x-j4p5
Type: github-advisory

## Affected
- RubyGems: `lawn-login` — affected 0.0.7

## Details
The login function in `lib/lawn.rb` in the lawn-login gem 0.0.7 for Ruby places credentials on the curl command line, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5000
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lawn-login/CVE-2014-5000.yml
- https://github.com/skalnik/lawn-login
- https://web.archive.org/web/20200229060607/http://www.vapid.dhs.org/advisories/lawn-login-0.0.7.html
