# [H] SysReptor Susceptible to Privilege Escalation by Authenticated Users

## Summary
Severity: High
Advisory: CVE-2025-59945
Aliases: GHSA-r6hm-59cq-gjg6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-27
Source: https://osv.dev/vulnerability/CVE-2025-59945
Type: osv

## Details
SysReptor is a fully customizable pentest reporting platform. In versions from 2024.74 to before 2025.83, authenticated and unprivileged (non-admin) users can assign the is_project_admin permission to their own user. This allows users to read, modify and delete pentesting projects they are not members of and are therefore not supposed to access. This issue has been patched in version 2025.83.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59945.json
- https://github.com/Syslifters/sysreptor/security/advisories/GHSA-r6hm-59cq-gjg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-59945
- https://github.com/Syslifters/sysreptor/commit/de8b5d89d0644479ee0da0a113c6bcc2436ba7f4
