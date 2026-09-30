# [M] Wallos: Authenticated Missing Authorization Allows Deletion of Other Users’ Uploaded Avatars

## Summary
Severity: Medium
Advisory: CVE-2026-30842
Aliases: GHSA-qw24-3pxr-3j6r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-30842
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.6.2, Wallos allows an authenticated user to delete avatar files uploaded by other users. The avatar deletion endpoint does not verify that the requested avatar belongs to the current user. As a result, any authenticated user who knows or can discover another user's uploaded avatar filename can delete that file. This issue has been patched in version 4.6.2.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30842.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-qw24-3pxr-3j6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-30842
- https://github.com/ellite/Wallos/commit/e8a513591dbbf885966e2ef55c38622785b9060d
