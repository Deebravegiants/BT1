# [H] Arbitrary File Deletion in eosphoros-ai/DB-GPT

## Summary
Severity: High
Advisory: CVE-2025-0452
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-0452
Type: osv

## Details
eosphoros-ai/DB-GPT version latest is vulnerable to arbitrary file deletion on Windows systems via the '/v1/agent/hub/update' endpoint. The application fails to properly filter the '\' character, which is commonly used as a separator in Windows paths. This vulnerability allows attackers to delete any files on the host system by manipulating the 'plugin_repo_name' variable.

## References
- https://huntr.com/bounties/7e854343-3d61-47d4-ad41-c4d2f356a54a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0452.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0452
