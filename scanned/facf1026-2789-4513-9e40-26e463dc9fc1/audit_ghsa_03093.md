# [H] HTTP Request Smuggling in goliath

## Summary
Severity: High
Advisory: GHSA-3892-2r52-p65m
CVE: CVE-2020-7671
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-3892-2r52-p65m
Type: github-advisory

## Affected
- RubyGems: `goliath` — affected >=0

## Details
goliath through 1.0.6 allows request smuggling attacks where goliath is used as a backend and a frontend proxy also being vulnerable. It is possible to conduct HTTP request smuggling attacks by sending the Content-Length header twice. Furthermore, invalid Transfer Encoding headers were found to be parsed as valid which could be leveraged for TE:CL smuggling attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7671
- https://github.com/postrank-labs/goliath/issues/351
- https://github.com/postrank-labs/goliath
- https://snyk.io/vuln/SNYK-RUBY-GOLIATH-569136
