# [H] FreePBX: Authenticated Local File Inclusion in Dashboard Module

## Summary
Severity: High
Advisory: CVE-2026-44239
Aliases: GHSA-hw7v-v2jp-wc4v
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44239
Type: osv

## Details
FreePBX is an open source IP PBX. Prior to 16.0.22 and 17.0.5, the Dashboard module's getcontent AJAX handler includes PHP files based on user-supplied input without path sanitization. The $_REQUEST['rawname'] parameter is concatenated into an include() call with a .class.php suffix, allowing path traversal via ../ sequences to include arbitrary .class.php files from the filesystem. The included file's PHP code executes before the subsequent class instantiation error occurs. This vulnerability is fixed in 16.0.22 and 17.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44239.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-hw7v-v2jp-wc4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44239
