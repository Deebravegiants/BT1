# [C] Bootstrap-sass contains code execution backdoor

## Summary
Severity: Critical
Advisory: GHSA-vqqv-v9m2-48p2
CVE: CVE-2019-10842
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-04
Source: https://github.com/advisories/GHSA-vqqv-v9m2-48p2
Type: github-advisory

## Affected
- RubyGems: `bootstrap-sass` — affected >=3.2.0.3 <3.2.0.4

## Details
Arbitrary code execution (via backdoor code) was discovered in bootstrap-sass 3.2.0.3, when downloaded from rubygems.org. An unauthenticated attacker can craft the ___cfduid cookie value with base64 arbitrary code to be executed via eval(), which can be leveraged to execute arbitrary code on the target system. Note that there are three underscore characters in the cookie name. This is unrelated to the __cfduid cookie that is legitimately used by Cloudflare.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10842
- https://github.com/twbs/bootstrap-sass/issues/1195
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bootstrap-sass/CVE-2019-10842.yml
- https://github.com/twbs/bootstrap-sass
- https://snyk.io/blog/malicious-remote-code-execution-backdoor-discovered-in-the-popular-bootstrap-sass-ruby-gem
- https://snyk.io/vuln/SNYK-RUBY-BOOTSTRAPSASS-174093
