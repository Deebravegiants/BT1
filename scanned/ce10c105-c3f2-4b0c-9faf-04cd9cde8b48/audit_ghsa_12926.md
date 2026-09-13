# [H] Devise Gem for Ruby Unauthorized Access Using "Remember Me" Cookie

## Summary
Severity: High
Advisory: GHSA-746g-3gfp-hfhw
CVE: CVE-2015-8314
CWE: CWE-288, CWE-312
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-746g-3gfp-hfhw
Type: github-advisory

## Affected
- RubyGems: `devise` — affected >=0 <3.5.4

## Details
Devise version before 3.5.4 uses cookies to implement a "Remember me" functionality. However, it generates the same cookie for all devices. If an attacker manages to steal a remember me cookie and the user does not change the password frequently, the cookie can be used to gain access to the application indefinitely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8314
- https://github.com/heartcombo/devise/commit/c92996646aba2d25b2c3e235fe0c4f1a84b70d24
- https://github.com/advisories/GHSA-746g-3gfp-hfhw
- https://github.com/heartcombo/devise
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise/CVE-2015-8314.yml
- https://rubysec.com/advisories/CVE-2015-8314
- http://blog.plataformatec.com.br/2016/01/improve-remember-me-cookie-expiration-in-devise
