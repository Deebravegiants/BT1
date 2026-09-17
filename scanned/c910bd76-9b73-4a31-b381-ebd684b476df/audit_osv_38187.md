# [C] Chyrp Lite has a Path Traversal to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-35174
Aliases: GHSA-p6pf-2grm-8257
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35174
Type: osv

## Details
Chyrp Lite is an ultra-lightweight blogging engine. Prior to 2026.01, a path traversal vulnerability exists in the administration console that allows an administrator or a user with Change Settings permission to change the uploads path to any folder. This vulnerability allows the user to download any file on the server, including config.json.php with database credentials and overwrite critical system files, leading to remote code execution. This vulnerability is fixed in 2026.01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35174.json
- https://github.com/xenocrat/chyrp-lite/security/advisories/GHSA-p6pf-2grm-8257
- https://nvd.nist.gov/vuln/detail/CVE-2026-35174
