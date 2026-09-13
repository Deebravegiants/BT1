# [M] open-webui Insecure Direct Object Reference (IDOR) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xcvc-5hgv-phqg
CVE: CVE-2024-7041
CWE: CWE-250, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-xcvc-5hgv-phqg
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
An Insecure Direct Object Reference (IDOR) vulnerability exists in open-webui/open-webui version v0.3.8. The vulnerability occurs in the API endpoint `http://0.0.0.0:3000/api/v1/memories/{id}/update`, where the decentralization design is flawed, allowing attackers to edit other users' memories without proper authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7041
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/main/backend/apps/webui/routers/memories.py#L71
- https://huntr.com/bounties/6855227f-1237-47b8-8d37-29aad7ddec3a
