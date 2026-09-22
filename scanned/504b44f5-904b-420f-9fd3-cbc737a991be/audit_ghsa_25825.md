# [C] Possible code injection vulnerability in Rails / Active Storage

## Summary
Severity: Critical
Advisory: GHSA-w749-p3v6-hccq
CVE: CVE-2022-21831
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-08
Source: https://github.com/advisories/GHSA-w749-p3v6-hccq
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=5.2.0 <5.2.6.3
- RubyGems: `activestorage` — affected >=6.0.0 <6.0.4.7
- RubyGems: `activestorage` — affected >=6.1.0 <6.1.4.7
- RubyGems: `activestorage` — affected >=7.0.0 <7.0.2.3

## Details
The Active Storage module of Rails starting with version 5.2.0 is possibly vulnerable to code injection. This issue was patched in versions 5.2.6.3, 6.0.4.7, 6.1.4.7, and 7.0.2.3. To work around this issue, applications should implement a strict allow-list on accepted transformation methods or arguments.  Additionally, a strict ImageMagick security policy will help mitigate this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21831
- https://github.com/rails/rails/commit/0a72f7d670e9aa77a0bb8584cb1411ddabb7546e
- https://github.com/advisories/GHSA-w749-p3v6-hccq
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2022-21831.yml
- https://groups.google.com/g/rubyonrails-security/c/n-p-W1yxatI
- https://lists.debian.org/debian-lts-announce/2022/09/msg00002.html
- https://rubysec.com/advisories/CVE-2022-21831
- https://security.netapp.com/advisory/ntap-20221118-0001
- https://www.debian.org/security/2023/dsa-5372
