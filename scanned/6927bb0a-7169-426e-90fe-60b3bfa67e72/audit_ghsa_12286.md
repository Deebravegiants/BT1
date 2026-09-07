# [M] omniauth-oauth2 Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fgmx-8h93-26fh
CVE: CVE-2012-6134
CWE: CWE-352
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-fgmx-8h93-26fh
Type: github-advisory

## Affected
- RubyGems: `omniauth-oauth2` — affected >=0 <1.1.1

## Details
Cross-site request forgery (CSRF) vulnerability in the omniauth-oauth2 gem prior to 1.1.1 for Ruby allows remote attackers to hijack the authentication of users for requests that modify session state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6134
- https://github.com/Shopify/omniauth-shopify-oauth2/pull/1
- https://github.com/intridea/omniauth-oauth2/pull/25
- https://github.com/Shopify/omniauth-shopify-oauth2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-oauth2/CVE-2012-6134.yml
- https://web.archive.org/web/20170312020947/https://gist.github.com/homakov/3673012
- http://rubysec.github.io/advisories/CVE-2012-6134
- http://seclists.org/oss-sec/2013/q1/304
