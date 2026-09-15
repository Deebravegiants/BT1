# [M] vantage6 Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-41882
Aliases: GHSA-gc57-xhh5-m94r, PYSEC-2023-201
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-10-11
Source: https://osv.dev/vulnerability/CVE-2023-41882
Type: osv

## Details
vantage6 is privacy preserving federated learning infrastructure. The endpoint /api/collaboration/{id}/task is used to collect all tasks from a certain collaboration. To get such tasks, a user should have permission to view the collaboration and to view the tasks in it. However, prior to version 4.0.0, it is only checked if the user has permission to view the collaboration. Version 4.0.0 contains a patch. There are no known workarounds.

## References
- https://github.com/vantage6/vantage6/blob/0682c4288f43fee5bcc72dc448cdd99bd7e57f76/docs/release_notes.rst#400
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41882.json
- https://github.com/vantage6/vantage6/security/advisories/GHSA-gc57-xhh5-m94r
- https://nvd.nist.gov/vuln/detail/CVE-2023-41882
- https://github.com/vantage6/vantage6/pull/711
