# [H] Local File Inclusion in imartinez/privategpt

## Summary
Severity: High
Advisory: CVE-2024-3403
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-3403
Type: osv

## Details
imartinez/privategpt version 0.2.0 is vulnerable to a local file inclusion vulnerability that allows attackers to read arbitrary files from the filesystem. By manipulating file upload functionality to ingest arbitrary local files, attackers can exploit the 'Search in Docs' feature or query the AI to retrieve or disclose the contents of any file on the system. This vulnerability could lead to various impacts, including but not limited to remote code execution by obtaining private SSH keys, unauthorized access to private files, source code disclosure facilitating further attacks, and exposure of configuration files.

## References
- https://huntr.com/bounties/7431d1dd-f014-4d4f-acb6-f97369ef3688
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3403.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3403
