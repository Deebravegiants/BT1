# [C] HAX CMS PHP allows Insecure File Upload to Lead to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-32028
Aliases: GHSA-vj5q-3jv2-cg5p
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-32028
Type: osv

## Details
HAX CMS PHP allows you to manage your microsite universe with PHP backend. Multiple file upload functions within the HAX CMS PHP application call a ’save’ function in ’HAXCMSFile.php’. This save function uses a denylist to block specific file types from being uploaded to the server. This list is non-exhaustive and only blocks ’.php’, ’.sh’, ’.js’, and ’.css’ files. The existing logic causes the system to "fail open" rather than "fail closed." This vulnerability is fixed in 10.0.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32028.json
- https://github.com/haxtheweb/issues/security/advisories/GHSA-vj5q-3jv2-cg5p
- https://nvd.nist.gov/vuln/detail/CVE-2025-32028
