# [C] Default user role exporting save state of instance

## Summary
Severity: Critical
Advisory: CVE-2024-0765
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-03-03
Source: https://osv.dev/vulnerability/CVE-2024-0765
Type: osv

## Details
As a default user on a multi-user instance of AnythingLLM, you could execute a call to the `/export-data` endpoint of the system and then unzip and read that export that would enable you do exfiltrate data of the system at that save state.

This would require the attacked to be granted explicit access to the system, but they can do this at any role. Additionally, post-download, the data is deleted so no evidence would exist that the exfiltration occured.

## References
- https://huntr.com/bounties/8978ab27-710c-44ce-bfd8-a2ea416dc786
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0765.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0765
- https://github.com/mintplex-labs/anything-llm/commit/08d33cfd8fc47c5052b6ea29597c964a9da641e2
