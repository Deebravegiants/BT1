# [H] Aim denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-36h2-g4c8-9xcm
CVE: CVE-2024-6227
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-36h2-g4c8-9xcm
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
A vulnerability in aimhubio/aim version 3.19.3 allows an attacker to cause an infinite loop by configuring the remote tracking server to point at itself. This results in the server endlessly connecting to itself, rendering it unable to respond to other connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6227
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/2e7b8aff8dcba9ddd5043dfec88cf2319ba8a87c/aim/sdk/repo.py#L195
- https://huntr.com/bounties/abcea7c6-bb3b-45e9-aa15-9eb6b224451a
