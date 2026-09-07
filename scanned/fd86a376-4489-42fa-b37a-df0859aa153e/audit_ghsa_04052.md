# [H] OmniAuth Ruby gem Cross-site Request Forgery in request phase

## Summary
Severity: High
Advisory: GHSA-ww4x-rwq6-qpgf
CVE: CVE-2015-9284
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-ww4x-rwq6-qpgf
Type: github-advisory

## Affected
- RubyGems: `omniauth` — affected >=0 <2.0.0

## Details
The request phase of the OmniAuth Ruby gem (1.9.2 and earlier) is vulnerable to Cross-Site Request Forgery when used as part of the Ruby on Rails framework, allowing accounts to be connected without user intent, user interaction, or feedback to the user. This permits a secondary account to be able to sign into the web application as the primary account.

As of v2 OmniAuth no longer has the vulnerable configuration by default, but it is still possible to configure OmniAuth in such a way that the web application becomes vulnerable to Cross-Site Request Forgery. There is a recommended remediation described [here](https://github.com/omniauth/omniauth/wiki/Resolving-CVE-2015-9284).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9284
- https://github.com/omniauth/omniauth/issues/1031
- https://github.com/omniauth/omniauth-rails/pull/1
- https://github.com/omniauth/omniauth/pull/809
- https://github.com/rubysec/ruby-advisory-db/commit/aef9f623c0be838234d53baf18977564804da397
- https://github.com/omniauth/omniauth
- https://github.com/omniauth/omniauth/releases/tag/v1.9.2
- https://github.com/omniauth/omniauth/releases/tag/v2.0.0
- https://github.com/omniauth/omniauth/wiki/Resolving-CVE-2015-9284
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth/CVE-2015-9284.yml
- https://www.openwall.com/lists/oss-security/2015/05/26/11
