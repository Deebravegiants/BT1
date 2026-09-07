# [H] Craft CMS Feed-Me

## Summary
Severity: High
Advisory: GHSA-6p78-f7h9-6838
CVE: CVE-2023-36260
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-6p78-f7h9-6838
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <4.6.2

## Details
An issue discovered in Craft CMS version 4.6.1.1 allows remote attackers to cause a denial of service (DoS) via crafted string to Feed-Me Name and Feed-Me URL fields due to saving a feed using an Asset element type with no volume selected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36260
- https://github.com/craftcms/feed-me/commit/b5d6ede51848349bd91bc95fec288b6793f15e28
- https://github.com/craftcms/feed-me/commit/b5d6ede51848349bd91bc95fec288b6793f15e28%29
- https://github.com/craftcms/feed-me
- https://github.com/craftcms/feed-me/releases/tag/4.6.2
- https://www.linkedin.com/pulse/threat-briefing-craftcms-amrcybersecurity-emi0e/?trackingId=E75GttWvQp6gfvPiJDDUBA%3D%3D
