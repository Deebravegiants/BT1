# [H] Chamilo LMS: Authenticated RCE via H5P Import

## Summary
Severity: High
Advisory: CVE-2026-30875
Aliases: GHSA-mj4f-8fw2-hrfm
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-30875
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to version 1.11.36, an arbitrary file upload vulnerability in the H5P Import feature allows authenticated users with Teacher role to achieve Remote Code Execution (RCE). The H5P package validation only checks if h5p.json exists but doesn't block .htaccess or PHP files with alternative extensions. An attacker uploads a crafted H5P package containing a webshell and .htaccess that enables PHP execution for .txt files, bypassing security control. This issue has been patched in version 1.11.36.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30875.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-mj4f-8fw2-hrfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-30875
