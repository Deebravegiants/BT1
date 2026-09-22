# [H] jruby-openssl gem for JRuby fails to do proper certificate validation

## Summary
Severity: High
Advisory: GHSA-xgv7-pqqh-h2w9
CVE: CVE-2009-4123
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-19
Source: https://github.com/advisories/GHSA-xgv7-pqqh-h2w9
Type: github-advisory

## Affected
- RubyGems: `jruby-openssl` — affected >=0 <0.6

## Details
A security problem involving peer certificate verification was found where failed verification silently did nothing, making affected applications vulnerable to attackers. Attackers could lead a client application to believe that a secure connection to a rogue SSL server is legitimate. Attackers could also penetrate client-validated SSL server applications with a dummy certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4123
- https://github.com/advisories/GHSA-xgv7-pqqh-h2w9
- https://github.com/jruby/jruby-openssl
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jruby-openssl/CVE-2009-4123.yml
- https://web.archive.org/web/20101213091125/http://jruby.org/2009/12/07/vulnerability-in-jruby-openssl
- http://jruby.org/2009/12/07/vulnerability-in-jruby-openssl
