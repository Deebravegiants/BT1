# [M] Path Traversal in binary-husky/gpt_academic

## Summary
Severity: Medium
Advisory: CVE-2024-10100
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-17
Source: https://osv.dev/vulnerability/CVE-2024-10100
Type: osv

## Details
A path traversal vulnerability exists in binary-husky/gpt_academic version 3.83. The vulnerability is due to improper handling of the file parameter, which is open to path traversal through URL encoding. This allows attackers to view any file on the host system, including sensitive files such as critical application files, SSH keys, API keys, and configuration values.

## References
- https://huntr.com/bounties/e58a0fb4-2b1d-49ef-b32e-bb62659a6f99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10100.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10100
