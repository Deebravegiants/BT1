# [M] Unrestricted File Upload and Execution in parisneo/lollms-webui

## Summary
Severity: Medium
Advisory: CVE-2024-9920
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9920
Type: osv

## Details
In version v12 of parisneo/lollms-webui, the 'Send file to AL' function allows uploading files with various extensions, including potentially dangerous ones like .py, .sh, .bat, and more. Attackers can exploit this by uploading files with malicious content and then using the '/open_file' API endpoint to execute these files. The vulnerability arises from the use of 'subprocess.Popen' to open files without proper validation, leading to potential remote code execution.

## References
- https://huntr.com/bounties/c70c6732-23b3-4ef8-aec6-0a47467d1ed5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9920.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9920
