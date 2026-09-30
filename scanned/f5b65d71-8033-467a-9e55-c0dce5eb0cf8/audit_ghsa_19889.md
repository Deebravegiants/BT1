# [M] Open WebUI Has Improper Access Control Leading to Arbitrary Prompt Read

## Summary
Severity: Medium
Advisory: GHSA-c7fq-p62p-wvpc
CVE: CVE-2024-7045
CWE: CWE-1100, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-c7fq-p62p-wvpc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version v0.3.8 of open-webui/open-webui, improper access control vulnerabilities allow an attacker to view any prompts. The application does not verify whether the attacker is an administrator, allowing the attacker to directly call the /api/v1/prompts/ interface to retrieve all prompt information created by the admin, which includes the ID values. Subsequently, the attacker can exploit the /api/v1/prompts/command/{command_id} interface to obtain arbitrary prompt information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7045
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/03ea0826-af7b-4717-b63e-90fd19675ab2
