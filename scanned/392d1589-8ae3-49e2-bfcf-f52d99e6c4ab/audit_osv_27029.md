# [H] Relative Path Traversal in mintplex-labs/anything-llm

## Summary
Severity: High
Advisory: CVE-2024-0549
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-0549
Type: osv

## Details
mintplex-labs/anything-llm is vulnerable to a relative path traversal attack, allowing unauthorized attackers with a default role account to delete files and folders within the filesystem, including critical database files such as 'anythingllm.db'. The vulnerability stems from insufficient input validation and normalization in the handling of file and folder deletion requests. Successful exploitation results in the compromise of data integrity and availability.

## References
- https://huntr.com/bounties/fcb4001e-0290-4b78-a2f0-91ee5d20cc72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0549.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0549
- https://github.com/mintplex-labs/anything-llm/commit/026849df0224b6a8754f4103530bc015874def62
