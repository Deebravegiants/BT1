# [M] Path Traversal in audiobookshelf

## Summary
Severity: Medium
Advisory: CVE-2024-43797
Aliases: GHSA-gg56-vj58-g5mc
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-02
Source: https://osv.dev/vulnerability/CVE-2024-43797
Type: osv

## Details
audiobookshelf is a self-hosted audiobook and podcast server. A non-admin user is not allowed to create libraries (or access only the ones they have permission to). However, the `LibraryController` is missing the check for admin user and thus allows a path traversal issue. Allowing non-admin users to write to any directory in the system can be seen as a form of path traversal. However, since it can be restricted to only admin permissions, fixing this is relatively simple and falls more into the realm of Role-Based Access Control (RBAC). This issue has been addressed in release version 2.13.0. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/advplyr/audiobookshelf/blob/1c0d6e9c670ebb1b6f1e427a4c4d9250a7fb9b80/server/controllers/LibraryController.js#L43-L47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43797.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-gg56-vj58-g5mc
- https://nvd.nist.gov/vuln/detail/CVE-2024-43797
- https://github.com/advplyr/audiobookshelf-ghsa-gg56-vj58-g5mc/pull/1
