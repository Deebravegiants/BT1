# [M] LinkAce: Authorization Bypass Allows Unauthorized Access to All Private Links, Lists, and Tags

## Summary
Severity: Medium
Advisory: CVE-2025-62721
Aliases: GHSA-47g2-qw6q-cr96
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-04
Source: https://osv.dev/vulnerability/CVE-2025-62721
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. In versions 2.3.1 and below, authenticated RSS feed endpoints in the FeedController class fail to implement proper authorization checks, allowing any authenticated user to access all links, lists, and tags from all users in the system, regardless of their ownership or visibility settings. This issue is fixed in version 2.4.0.

## References
- https://github.com/Kovah/LinkAce/releases/tag/v2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62721.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-47g2-qw6q-cr96
- https://nvd.nist.gov/vuln/detail/CVE-2025-62721
- https://github.com/Kovah/LinkAce/commit/1fef32694cee2bd80892fb478416be9364c3fddd
