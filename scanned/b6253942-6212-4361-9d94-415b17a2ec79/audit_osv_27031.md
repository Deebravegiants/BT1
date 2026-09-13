# [H] Download and export of file via default user role

## Summary
Severity: High
Advisory: CVE-2024-0551
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2024-0551
Type: osv

## Details
Enable exports of the database and associated exported information of the system via the default user role. The attacked would have to have been granted access to the system prior to the attack.

It is worth noting that the deterministic nature of the export name is lower risk as the UI for exporting would start the download at the same time, which once downloaded - deletes the export from the system.

The endpoint for exporting should simply be patched to a higher privilege level.

## References
- https://huntr.com/bounties/f114c787-ab5f-4f83-afa5-c000435efb78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0551.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0551
- https://github.com/mintplex-labs/anything-llm/commit/7aaa4b38e7112a6cd879c1238310c56b1844c6d8
