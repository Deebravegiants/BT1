# [H] Incorrect Authorization in mintplex-labs/anything-llm

## Summary
Severity: High
Advisory: CVE-2024-10109
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10109
Type: osv

## Details
A vulnerability in the mintplex-labs/anything-llm repository, as of commit 5c40419, allows low privilege users to access the sensitive API endpoint "/api/system/custom-models". This access enables them to modify the model's API key and base path, leading to potential API key leakage and denial of service on chats.

## References
- https://huntr.com/bounties/ad3c9e76-679d-4775-b203-96947ff73551
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10109.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10109
- https://github.com/mintplex-labs/anything-llm/commit/8d302c3f670c582b09d47e96132c248101447a11
