# [H] Open WebUI Allows Admin Deletion via API Endpoint

## Summary
Severity: High
Advisory: GHSA-pqwr-phvv-v49f
CVE: CVE-2024-7039
CWE: CWE-269, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-pqwr-phvv-v49f
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In open-webui/open-webui version v0.3.8, there is an improper privilege management vulnerability. The application allows an attacker, acting as an admin, to delete other administrators via the API endpoint `http://0.0.0.0:8080/api/v1/users/{uuid_administrator}`. This action is restricted by the user interface but can be performed through direct API calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7039
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/27fc8a5a-546e-4cf2-8edb-df42e36518fc
