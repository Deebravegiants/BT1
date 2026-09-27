# [H] Chamilo: Authenticated Remote Code Execution via Unrestricted File Upload

## Summary
Severity: High
Advisory: CVE-2026-29041
Aliases: GHSA-4pc3-4w2v-vwx8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29041
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.34, Chamilo LMS is affected by an authenticated remote code execution vulnerability caused by improper validation of uploaded files. The application relies solely on MIME-type verification when handling file uploads and does not adequately validate file extensions or enforce safe server-side storage restrictions. As a result, an authenticated low-privileged user can upload a crafted file containing executable code and subsequently execute arbitrary commands on the server. This issue has been patched in version 1.11.34.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29041.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-4pc3-4w2v-vwx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-29041
