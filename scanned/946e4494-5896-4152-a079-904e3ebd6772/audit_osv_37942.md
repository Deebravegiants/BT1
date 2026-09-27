# [M] LinkAce discloses private notesto unauthorized authenticated users via the web link detail page

## Summary
Severity: Medium
Advisory: CVE-2026-33954
Aliases: GHSA-88h3-cq25-vw8q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33954
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. In versions prior to 2.5.3, a private note attached to a non-private link can be disclosed to a different authenticated user via the web interface. The API appears to correctly enforce note visibility, but the web link detail page renders notes without applying equivalent visibility filtering. As a result, an authenticated user who is allowed to view another user's `internal` or `public` link can read that user's `private` notes attached to the link. Version 2.5.3 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33954.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-88h3-cq25-vw8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33954
