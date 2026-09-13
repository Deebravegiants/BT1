# [M] newrelic_rpm Gem Discloses Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-q6cw-2553-7837
CVE: CVE-2013-0284
CWE: CWE-200
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-q6cw-2553-7837
Type: github-advisory

## Affected
- RubyGems: `newrelic_rpm` — affected >=3.2.0 <3.5.3.24

## Details
Ruby agent 3.2.0 through 3.5.3.23 serializes sensitive data when communicating with servers operated by New Relic, which allows remote attackers to obtain sensitive information (database credentials and SQL statements) by sniffing the network and deserializing the data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0284
- https://github.com/newrelic/newrelic-ruby-agent
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/newrelic_rpm/CVE-2013-0284.yml
- https://newrelic.com/docs/ruby/ruby-agent-security-notification
- https://web.archive.org/web/20130117025417/https://newrelic.com/docs/ruby/ruby-agent-security-notification
- http://seclists.org/oss-sec/2013/q1/304
