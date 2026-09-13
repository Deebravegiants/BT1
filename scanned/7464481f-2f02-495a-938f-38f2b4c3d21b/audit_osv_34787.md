# [H] Rallly Improper Authorization in Comment Deletion Endpoint Allows Unauthorized Comment Removal

## Summary
Severity: High
Advisory: CVE-2025-65030
Aliases: GHSA-4j32-25f9-qgfm
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65030
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an authorization flaw in the comment deletion API allows any authenticated user to delete comments belonging to other users, including poll owners and administrators. The endpoint relies solely on the comment ID for deletion and does not validate whether the requesting user owns the comment or has permission to remove it. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65030.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-4j32-25f9-qgfm
- https://nvd.nist.gov/vuln/detail/CVE-2025-65030
