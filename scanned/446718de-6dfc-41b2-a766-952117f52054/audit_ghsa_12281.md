# [M] sentry-raven allows remote attackers to cause a denial of service via a large exponent value in a scientific number

## Summary
Severity: Medium
Advisory: GHSA-c9c5-9fpr-m882
CVE: CVE-2014-9490
CWE: CWE-400
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-c9c5-9fpr-m882
Type: github-advisory

## Affected
- RubyGems: `sentry-raven` — affected >=0 <0.12.2

## Details
The `numtok` function in `lib/raven/okjson.rb` in the raven-ruby gem before 0.12.2 for Ruby allows remote attackers to cause a denial of service via a large exponent value in a scientific number.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9490
- https://github.com/getsentry/raven-ruby/commit/477ee93a3f735be33bc1e726820654cdf6e22d8f
- https://exchange.xforce.ibmcloud.com/vulnerabilities/99687
- https://github.com/getsentry/raven-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sentry-raven/CVE-2014-9490.yml
- https://groups.google.com/forum/#!topic/getsentry/Cz5bih0ZY1U
- http://seclists.org/oss-sec/2015/q1/26
