# [H] Open WebUI Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-wcwp-9rcp-jvfg
CVE: CVE-2024-7036
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-wcwp-9rcp-jvfg
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
A vulnerability in open-webui/open-webui v0.3.8 allows an unauthenticated attacker to sign up with excessively large text in the 'name' field, causing the Admin panel to become unresponsive. This prevents administrators from performing essential user management actions such as deleting, editing, or adding users. The vulnerability can also be exploited by authenticated users with low privileges, leading to the same unresponsive state in the Admin panel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7036
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/ba62d093-ab27-48fa-9c53-0602c8cdc48a
