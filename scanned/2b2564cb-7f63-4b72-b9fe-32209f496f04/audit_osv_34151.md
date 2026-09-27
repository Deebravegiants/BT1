# [M] Part-DB Persistent Denial of Service via Uncaught Exception from Misleading File Extension in Avatar Upload

## Summary
Severity: Medium
Advisory: CVE-2025-55194
Aliases: GHSA-7rv3-rcxv-69ww
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-55194
Type: osv

## Details
Part-DB is an open source inventory management system for electronic components. Prior to version 1.17.3, any authenticated user can upload a profile picture with a misleading file extension (e.g., .jpg.txt), resulting in a persistent 500 Internal Server Error when attempting to view or edit that user’s profile. This makes the profile permanently inaccessible via the UI for both users and administrators, constituting a Denial of Service (DoS) within the user management interface. This issue has been patched in version 1.17.3.

## References
- https://drive.google.com/file/d/10exp_BS9kRKHrFSPjiA_ZYUVJbHN8doW/view
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55194.json
- https://github.com/Part-DB/Part-DB-server/security/advisories/GHSA-7rv3-rcxv-69ww
- https://nvd.nist.gov/vuln/detail/CVE-2025-55194
- https://github.com/Part-DB/Part-DB-server/commit/d370f976a7b0c19d502aadbaa0f93eb90c2a6ffa
