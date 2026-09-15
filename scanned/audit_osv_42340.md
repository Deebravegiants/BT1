# [C] Wolf CMS 0.8.3.1 Authenticated RCE via FileManagerController File Upload

## Summary
Severity: Critical
Advisory: CVE-2026-67206
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67206
Type: osv

## Details
Wolf CMS through 0.8.3.1 contains a remote code execution vulnerability in FileManagerController that allows authenticated attackers to create arbitrary PHP files by exploiting missing file extension validation in the create_file() and save() functions. Attackers with the file_manager_mkfile capability can write malicious PHP content into the web-accessible FILES_DIR directory and trigger execution by requesting the file over HTTP.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67206
- https://www.vulncheck.com/advisories/wolf-cms-authenticated-rce-via-filemanagercontroller-file-upload
- https://github.com/wolfcms/wolfcms
- https://github.com/Caycon/cve-advisories/blob/main/2026/WolfCms/CVE-2026-67206.md
