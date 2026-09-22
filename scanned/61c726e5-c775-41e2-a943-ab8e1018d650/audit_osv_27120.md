# [H] Path Traversal in eosphoros-ai/db-gpt

## Summary
Severity: High
Advisory: CVE-2024-10830
Aliases: GHSA-8pwp-phcg-h36g, PYSEC-2026-1291
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10830
Type: osv

## Details
A Path Traversal vulnerability exists in the eosphoros-ai/db-gpt version 0.6.0 at the API endpoint `/v1/resource/file/delete`. This vulnerability allows an attacker to delete any file on the server by manipulating the `file_key` parameter. The `file_key` parameter is not properly sanitized, enabling an attacker to specify arbitrary file paths. If the specified file exists, the application will delete it.

## References
- https://huntr.com/bounties/26adf08a-9262-4d5a-a2ee-ce12ed919620
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10830.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10830
