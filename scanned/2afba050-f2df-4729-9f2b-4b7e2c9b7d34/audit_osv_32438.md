# [H] NamelessMC Forum iframe width/height abuse causing UI-based Denial of Service

## Summary
Severity: High
Advisory: CVE-2025-30158
Aliases: GHSA-2prx-rgr7-hq5f
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-30158
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. In version 2.1.4 and prior, the forum allows users to post iframe elements inside forum topics/comments/feed with no restriction on the iframe's width and height attributes. This allows an authenticated attacker to perform a UI-based denial of service (DoS) by injecting oversized iframes that block the forum UI and disrupt normal user interactions. This issue has been patched in version 2.2.0.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30158.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-2prx-rgr7-hq5f
- https://nvd.nist.gov/vuln/detail/CVE-2025-30158
- https://github.com/NamelessMC/Nameless/commit/caa42a975338a13fbc1658e8c440108f16135643
