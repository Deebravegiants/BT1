# [M] Actionpack Open Redirect Vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-8877-prq4-9xfw
CVE: CVE-2021-22881
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-02
Source: https://github.com/advisories/GHSA-8877-prq4-9xfw
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.5
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.2.1

## Details
The Host Authorization middleware in Action Pack before 6.1.2.1, 6.0.3.5 suffers from an open redirect vulnerability. Specially crafted `Host` headers in combination with certain "allowed host" formats can cause the Host Authorization middleware in Action Pack to redirect users to a malicious website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22881
- https://github.com/rails/rails/commit/b5de7b3a4787d8a55aaad39f477c16e3af65e444
- https://hackerone.com/reports/1047447
- https://benjamin-bouchet.com/cve-2021-22881-faille-de-securite-dans-le-middleware-hostauthorization
- https://discuss.rubyonrails.org/t/cve-2021-22881-possible-open-redirect-in-host-authorization-middleware/77130
- https://github.com/rails/rails
- https://github.com/rails/rails/blob/v6.1.2.1/actionpack/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-22881.yml
- https://groups.google.com/g/rubyonrails-security/c/zN_3qA26l6E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XQ3NS4IBYE2I3MVMGAHFZBZBIZGHXHT3
- https://rubygems.org/gems/actionpack
- http://www.openwall.com/lists/oss-security/2021/05/05/2
- http://www.openwall.com/lists/oss-security/2021/08/20/1
- http://www.openwall.com/lists/oss-security/2021/12/14/5
