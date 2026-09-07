# [H] Spina gem vulnerable to Cross-site request forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-2hxv-mx8x-mcj9
CVE: CVE-2015-4619
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-28
Source: https://github.com/advisories/GHSA-2hxv-mx8x-mcj9
Type: github-advisory

## Affected
- RubyGems: `spina` — affected >=0 <0.6.29

## Details
Cross-site request forgery (CSRF) vulnerability in Spina before commit bfe44f289e336f80b6593032679300c493735e75. `Spina::ApplicationController` actions didn't have CSRF protection. This causes a CSRF vulnerability across the entire engine which includes administrative functionality such as creating users, changing passwords, and media management.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4619
- https://github.com/denkGroot/Spina/commit/bfe44f289e336f80b6593032679300c493735e75
- https://github.com/denkGroot/Spina
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spina/CVE-2015-4619.yml
- http://www.openwall.com/lists/oss-security/2015/06/16/11
- http://www.openwall.com/lists/oss-security/2015/06/16/20
- http://www.securityfocus.com/bid/75216
