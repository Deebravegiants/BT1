# [M] Gogs: Authorization Bypass in Watch API allows any user to monitor private repository activity

## Summary
Severity: Medium
Advisory: CVE-2026-52795
Aliases: GHSA-v8w7-f6gc-cqc2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52795
Type: osv

## Details
Gogs is an open source self-hosted Git service. In 0.14.3 and earlier, any authenticated user can watch a private repository they have no access to, because the access check in the Watch API handler is inverted. The code checks if repoCtx.ViewerCanRead() (returns 404 when the user CAN read) instead of if !repoCtx.ViewerCanRead() (return 404 when the user CANNOT read). Once watching, the attacker's dashboard activity feed shows commit messages, branch names, issue titles, and PR details from the private repository. If email notifications are enabled, the attacker also receives emails containing issue and comment content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52795.json
- https://github.com/gogs/gogs/security/advisories/GHSA-v8w7-f6gc-cqc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-52795
- https://github.com/gogs/gogs/commit/d61caa3676fde060d0c03ccf815851dddc7c67e0
