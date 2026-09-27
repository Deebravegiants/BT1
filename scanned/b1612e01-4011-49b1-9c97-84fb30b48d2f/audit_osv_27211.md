# [H] Local File Inclusion in netease-youdao/qanything

## Summary
Severity: High
Advisory: CVE-2024-12866
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12866
Type: osv

## Details
A local file inclusion vulnerability exists in netease-youdao/qanything version v2.0.0. This vulnerability allows an attacker to read arbitrary files on the file system, which can lead to remote code execution by retrieving private SSH keys, reading private files, source code, and configuration files.

## References
- https://huntr.com/bounties/c23da7c7-a226-40a2-83db-6a8ab1b2ef64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12866.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12866
