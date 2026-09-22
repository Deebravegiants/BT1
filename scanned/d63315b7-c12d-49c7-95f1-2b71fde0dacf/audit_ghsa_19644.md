# [H] Aim Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-j5qj-rg5j-j7c2
CVE: CVE-2025-0189
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-j5qj-rg5j-j7c2
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
In version 3.25.0 of aimhubio/aim, the tracking server is vulnerable to a denial of service attack. The server overrides the maximum size for websocket messages, allowing very large images to be tracked. This causes the server to become unresponsive to other requests while processing the large image, leading to a denial of service condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0189
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/e4c9bf41-72cf-4d04-baaf-8f12b5b7926e
