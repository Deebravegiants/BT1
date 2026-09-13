# [C] CVE-2024-55371

## Summary
Severity: Critical
Advisory: CVE-2024-55371
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2024-55371
Type: osv

## Details
Wallos <= 2.38.2 has a file upload vulnerability in the restore backup function, which allows authenticated users to restore backups by uploading a ZIP file. The contents of the ZIP file are extracted on the server. This functionality enables an authenticated attacker (being an administrator is not required) to upload malicious files to the server. Once a web shell is installed, the attacker gains the ability to execute arbitrary commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55371.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55371
- https://www.datafarm.co.th/blog/CVE-2024-55371-and-CVE-2024-55372-Malicious-File-Upload-to-RCE-in-Wallos-Application
