# [M] In plane.io, a Guest User to a Workspace can still be able to see list of members

## Summary
Severity: Medium
Advisory: CVE-2025-69284
Aliases: GHSA-7qx6-6739-c7qr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-02
Source: https://osv.dev/vulnerability/CVE-2025-69284
Type: osv

## Details
Plane is an an open-source project management tool. In plane.io, a guest user doesn't have a permission to access https[:]//app[.]plane[.]so/[:]slug/settings. Prior to Plane version 1.2.0, a problem occurs when the `/api/workspaces/:slug/members/` is accessible by guest and able to list of users on a specific workspace that they joined. Since the `display_name` in the response is actually the handler of the email, a malicious guest can still identify admin users' email addresses. Version 1.2.0 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69284.json
- https://github.com/makeplane/plane/security/advisories/GHSA-7qx6-6739-c7qr
- https://nvd.nist.gov/vuln/detail/CVE-2025-69284
