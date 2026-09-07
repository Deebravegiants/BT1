# [M] AgentScope stored cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6mf6-7j75-2m6f
CVE: CVE-2024-8556
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6mf6-7j75-2m6f
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability exists in modelscope/agentscope, as of the latest commit 21161fe on the main branch. The vulnerability occurs in the view for inspecting detailed run information, where a user-controllable string (run ID) is appended and rendered as HTML. This allows an attacker to execute arbitrary JavaScript code in the context of the user's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8556
- https://github.com/modelscope/agentscope
- https://github.com/modelscope/agentscope/blob/21161fe9985ee2a2f617180b00a1424b81302d42/src/agentscope/studio/static/js/dashboard.js#L90
- https://huntr.com/bounties/8439f16b-5256-4466-bb7d-371572572a4b
