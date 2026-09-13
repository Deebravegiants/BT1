# [C] Server-Side Template Injection in Camaleon CMS

## Summary
Severity: Critical
Advisory: GHSA-x487-866m-p8hr
CVE: CVE-2023-30145
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-x487-866m-p8hr
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=0 <2.7.4

## Details
Camaleon CMS prior to 2.7.4 was discovered to contain a Server-Side Template Injection (SSTI) vulnerability via the `formats` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30145
- https://github.com/owen2345/camaleon-cms/issues/1052
- https://github.com/owen2345/camaleon-cms/commit/4485788c544eb1aae52ca613bd9626129e3df6ee
- https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection
- https://drive.google.com/file/d/11MsSYqUnDRFjcwbQKJeL9Q8nWpgVYf2r/view?usp=share_link
- https://github.com/owen2345/camaleon-cms
- https://github.com/owen2345/camaleon-cms/releases/tag/2.7.4
- https://github.com/paragbagul111/CVE-2023-30145
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2023-30145.yml
- https://portswigger.net/research/server-side-template-injection
- http://packetstormsecurity.com/files/172593/Camaleon-CMS-2.7.0-Server-Side-Template-Injection.html
