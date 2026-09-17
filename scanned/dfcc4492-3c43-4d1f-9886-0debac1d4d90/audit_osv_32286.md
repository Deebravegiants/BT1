# [H] Privilege escalation in Joplin server via user patch endpoint

## Summary
Severity: High
Advisory: CVE-2025-27134
Aliases: GHSA-xj67-649m-3p8x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-30
Source: https://osv.dev/vulnerability/CVE-2025-27134
Type: osv

## Details
Joplin is a free, open source note taking and to-do application, which can handle a large number of notes organised into notebooks. Prior to version 3.3.3, a privilege escalation vulnerability exists in the Joplin server, allowing non-admin users to exploit the API endpoint `PATCH /api/users/:id` to set the `is_admin` field to 1. The vulnerability allows malicious low-privileged users to perform administrative actions without proper authorization. This issue has been patched in version 3.3.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27134.json
- https://github.com/laurent22/joplin/security/advisories/GHSA-xj67-649m-3p8x
- https://nvd.nist.gov/vuln/detail/CVE-2025-27134
- https://github.com/laurent22/joplin/commit/12baa9827dac9da903f244c9f358e3deb264e228
