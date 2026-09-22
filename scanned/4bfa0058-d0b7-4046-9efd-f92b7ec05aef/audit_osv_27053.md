# [H] Improper validation of document removal parameter

## Summary
Severity: High
Advisory: CVE-2024-0763
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2024-0763
Type: osv

## Details
Any user can delete an arbitrary folder (recursively) on a remote server due to bad input sanitization leading to path traversal. The attacker would need access to the server at some privilege level since this endpoint is protected and requires authorization.

## References
- https://huntr.com/bounties/25a2f487-5a9c-4c7f-a2d3-b0527db73ea5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0763.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0763
- https://github.com/mintplex-labs/anything-llm/commit/8a7324d0e77a15186e1ad5e5119fca4fb224c39c
