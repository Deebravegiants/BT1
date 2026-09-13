# [M] Camaleon CMS vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-vx6p-q4gj-x6xx
CVE: CVE-2021-25972
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vx6p-q4gj-x6xx
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=2.1.2.0 <2.6.0.1

## Details
In Camaleon CMS, versions 2.1.2.0 through 2.6.0, are vulnerable to Server-Side Request Forgery (SSRF) in the media upload feature, which allows admin users to fetch media files from external URLs but fails to validate URLs referencing to localhost or other internal servers. This allows attackers to read files stored in the internal server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25972
- https://github.com/owen2345/camaleon-cms/commit/5a252d537411fdd0127714d66c1d76069dc7e190
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2021-25972.yml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25972
