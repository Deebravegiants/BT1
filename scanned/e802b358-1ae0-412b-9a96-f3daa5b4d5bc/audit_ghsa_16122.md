# [M] Sinatra vulnerable to Reliance on Untrusted Inputs in a Security Decision

## Summary
Severity: Medium
Advisory: GHSA-hxx2-7vcw-mqr3
CVE: CVE-2024-21510
CWE: CWE-807
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-01
Source: https://github.com/advisories/GHSA-hxx2-7vcw-mqr3
Type: github-advisory

## Affected
- RubyGems: `sinatra` — affected >=0 <4.1.0

## Details
Versions of the package sinatra from 0.0.0 are vulnerable to Reliance on Untrusted Inputs in a Security Decision via the X-Forwarded-Host (XFH) header. When making a request to a method with redirect applied, it is possible to trigger an Open Redirect Attack by inserting an arbitrary address into this header. If used for caching purposes, such as with servers like Nginx, or as a reverse proxy, without handling the X-Forwarded-Host header, attackers can potentially exploit Cache Poisoning or Routing-based SSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21510
- https://github.com/sinatra/sinatra/pull/2010
- https://github.com/advisories/GHSA-hxx2-7vcw-mqr3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sinatra/CVE-2024-21510.yml
- https://github.com/sinatra/sinatra
- https://github.com/sinatra/sinatra/blob/b626e2d82c23b4fde0b51782fd32ca27ccde1d1a/lib/sinatra/base.rb#L319
- https://github.com/sinatra/sinatra/blob/b626e2d82c23b4fde0b51782fd32ca27ccde1d1a/lib/sinatra/base.rb#L323C1-L343C17
- https://github.com/sinatra/sinatra/blob/main/CHANGELOG.md#410--2024-11-18
- https://security.snyk.io/vuln/SNYK-RUBY-SINATRA-6483832
