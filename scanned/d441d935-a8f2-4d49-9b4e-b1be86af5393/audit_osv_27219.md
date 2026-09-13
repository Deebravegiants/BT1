# [M] Improper Authorization in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-13060
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-13060
Type: osv

## Details
A vulnerability in AnythingLLM Docker version 1.3.1 allows users with 'Default' permission to access other users' profile pictures by changing the 'id' parameter in the user cookie. This issue is present in versions prior to 1.3.1.

## References
- https://huntr.com/bounties/98a49c90-e095-441f-900c-59d463dc8e8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/13xxx/CVE-2024-13060.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-13060
- https://github.com/mintplex-labs/anything-llm/commit/696af19c45473172ad4d3ca749281800a4d1a45a
