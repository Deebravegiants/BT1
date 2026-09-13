# [H] Gitea Web Attachment Deletion: Cross-Repository Unauthorized Deletion via Missing Repo Ownership Check

## Summary
Severity: High
Advisory: BIT-gitea-2026-20736
Aliases: CVE-2026-20736, GHSA-hgr3-x44x-33hx, GHSA-jr6h-pwwp-c8g6, GO-2026-4367
Ecosystem: Bitnami
Published: 2026-01-30
Source: https://osv.dev/vulnerability/BIT-gitea-2026-20736
Type: osv

## Affected
- Bitnami: `gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly verify repository context when deleting attachments. A user who previously uploaded an attachment to a repository may be able to delete it after losing access to that repository by making the request through a different repository they can access.

## References
- https://blog.gitea.com/release-of-1.25.4/
- https://github.com/go-gitea/gitea/pull/36320
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
- https://github.com/go-gitea/gitea/security/advisories/GHSA-jr6h-pwwp-c8g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-20736
- https://access.redhat.com/security/cve/CVE-2026-20736
- https://bugzilla.redhat.com/show_bug.cgi?id=2432205
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-20736.json
