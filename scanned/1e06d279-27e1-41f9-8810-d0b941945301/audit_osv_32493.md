# [M] NamelessMC Vulnerable to Cookie-Based View Count Manipulation

## Summary
Severity: Medium
Advisory: CVE-2025-31120
Aliases: GHSA-8jv7-77jw-h646
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-31120
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. In version 2.1.4 and prior, an insecure view count mechanism in the forum page allows an unauthenticated attacker to artificially increase the view count. The application relies on a client-side cookie (nl-topic-[tid]) (or session variable for guests) to determine if a view should be counted. When a client does not provide the cookie, every page request increments the counter, leading to incorrect view metrics. This issue has been patched in version 2.2.0.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31120.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-8jv7-77jw-h646
- https://nvd.nist.gov/vuln/detail/CVE-2025-31120
- https://github.com/NamelessMC/Nameless/commit/9b112c0beab346a38b6f5a51e7773b38c6fc52e7
