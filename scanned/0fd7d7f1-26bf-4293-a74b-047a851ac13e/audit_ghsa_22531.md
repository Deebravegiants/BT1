# [H] Elastic APM agent for Ruby vulnerable to Improper Certificate Validation

## Summary
Severity: High
Advisory: GHSA-35j2-p8fh-x966
CVE: CVE-2019-7615
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-35j2-p8fh-x966
Type: github-advisory

## Affected
- RubyGems: `elastic-apm` — affected >=0 <2.9.0

## Details
A TLS certificate validation flaw was found in Elastic APM agent for Ruby versions before 2.9.0. When specifying a trusted server CA certificate via the `server_ca_cert` setting, the Ruby agent would not properly verify the certificate returned by the APM server. This could result in a man in the middle style attack against the Ruby agent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7615
- https://github.com/elastic/apm-agent-ruby/pull/449
- https://github.com/elastic/apm-agent-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/elastic-apm/CVE-2019-7615.yml
- https://www.elastic.co/community/security
