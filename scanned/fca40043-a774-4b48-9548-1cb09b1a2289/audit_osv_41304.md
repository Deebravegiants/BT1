# [H] immich < 3.0.3 Shared Album Editor Ownership Takeover via updateUser

## Summary
Severity: High
Advisory: CVE-2026-59258
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-59258
Type: osv

## Details
immich before 3.0.3 contains a broken access control vulnerability in the PUT /albums/:id/user/:userId endpoint that allows shared album editors to modify member roles without owner-only restrictions. Attackers with editor access can demote the album owner to editor and promote themselves to owner in sequential requests, gaining full control including deletion and eviction capabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59258.json
- https://github.com/immich-app/immich/releases/tag/v3.0.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59258
- https://www.vulncheck.com/advisories/immich-shared-album-editor-ownership-takeover-via-updateuser
- https://github.com/immich-app/immich/pull/29883
- https://github.com/immich-app/immich/commit/84dff19ca9a467752d848ff54763d62c04ebf960
- https://github.com/immich-app/immich
- https://github.com/immich-app/immich/issues/29857
