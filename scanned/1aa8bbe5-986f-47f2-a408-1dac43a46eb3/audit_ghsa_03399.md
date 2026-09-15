# [H] Improper Certificate Validation in oauth ruby gem

## Summary
Severity: High
Advisory: GHSA-7359-3c6r-hfc2
CVE: CVE-2016-11086
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-7359-3c6r-hfc2
Type: github-advisory

## Affected
- RubyGems: `oauth` — affected >=0 <0.5.5

## Details
lib/oauth/consumer.rb in the oauth-ruby gem through 0.5.4 for Ruby does not verify server X.509 certificates if a certificate bundle cannot be found, which allows man-in-the-middle attackers to spoof servers and obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11086
- https://github.com/oauth-xx/oauth-ruby/issues/137
- https://github.com/oauth-xx/oauth-ruby/commit/eb5b00a91d4ef0899082fdba929c34ccad6d4ccb
- https://github.com/oauth-xx/oauth-ruby
- https://github.com/oauth-xx/oauth-ruby/releases/tag/v0.5.5
- https://rubygems.org/gems/oauth
