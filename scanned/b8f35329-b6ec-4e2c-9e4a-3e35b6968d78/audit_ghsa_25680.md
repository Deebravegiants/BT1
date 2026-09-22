# [C] Server side request forgery in gibbon

## Summary
Severity: Critical
Advisory: GHSA-vx9g-377x-xwxq
CVE: CVE-2022-27311
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-vx9g-377x-xwxq
Type: github-advisory

## Affected
- RubyGems: `gibbon` — affected >=0 <3.4.4

## Details
Gibbon v3.4.3 and below allows attackers to execute a Server-Side Request Forgery (SSRF) via a crafted URL. This issue has been resolved in version 3.4.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27311
- https://github.com/amro/gibbon/pull/321
- https://github.com/amro/gibbon/pull/321#issuecomment-1113147155
- https://github.com/amro/gibbon/commit/b2eb99ed304d7491a6d348a5bbdc83a008fc6e0b
- https://github.com/amro/gibbon/commit/cade20ca2438cd1b182dad70cbb77fb895779d10
- https://github.com/amro/gibbon
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/gibbon/CVE-2022-27311.yml
