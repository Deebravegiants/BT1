# [M] Devise Token Auth vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-mvqr-r76c-wm5f
CVE: CVE-2019-16751
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mvqr-r76c-wm5f
Type: github-advisory

## Affected
- RubyGems: `devise_token_auth` — affected >=0.1.33 <1.1.3

## Details
An issue was discovered in Devise Token Auth through 1.1.2. The omniauth failure endpoint is vulnerable to Reflected Cross Site Scripting (XSS) through the message parameter. Unauthenticated attackers can craft a URL that executes a malicious JavaScript payload in the victim's browser. This affects the `fallback_render` method in the omniauth callbacks controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16751
- https://github.com/lynndylanhurley/devise_token_auth/issues/1332
- https://github.com/lynndylanhurley/devise_token_auth
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise_token_auth/CVE-2019-16751.yml
