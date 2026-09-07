# [H] Open WebUI Allows Arbitrary File Reading and Deletion

## Summary
Severity: High
Advisory: GHSA-jrhc-9qg9-4qfq
CVE: CVE-2024-7043
CWE: CWE-821, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-jrhc-9qg9-4qfq
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
An improper access control vulnerability in open-webui/open-webui v0.3.8 allows attackers to view and delete any files. The application does not verify whether the attacker is an administrator, allowing the attacker to directly call the GET /api/v1/files/ interface to retrieve information on all files uploaded by users, which includes the ID values. The attacker can then use the GET /api/v1/files/{file_id} interface to obtain information on any file and the DELETE /api/v1/files/{file_id} interface to delete any file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7043
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/c01e0c7f-68d8-45cf-91d2-521c97f33b00
