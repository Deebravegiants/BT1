# [M] Open WebUI Allows Viewing of Admin Details

## Summary
Severity: Medium
Advisory: GHSA-gv26-qw3h-8qvp
CVE: CVE-2024-7046
CWE: CWE-475, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-gv26-qw3h-8qvp
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
An improper access control vulnerability in open-webui/open-webui v0.3.8 allows an attacker to view admin details. The application does not verify whether the attacker is an administrator, allowing the attacker to directly call the /api/v1/auths/admin/details interface to retrieve the first admin (owner) details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7046
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/684185e4-6766-4638-b08a-0de9c2820aee
