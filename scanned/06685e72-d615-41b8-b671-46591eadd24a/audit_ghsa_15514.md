# [M] Composio Code Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mrmh-3hqh-pfw7
CVE: CVE-2024-8864
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-mrmh-3hqh-pfw7
Type: github-advisory

## Affected
- PyPI: `composio-core` — affected >=0

## Details
A vulnerability has been found in composiohq composio up to 0.5.6 and classified as critical. Affected by this vulnerability is the function Calculator of the file python/composio/tools/local/mathematical/actions/calculator.py. The manipulation leads to code injection. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8864
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/blob/v0.5.6/python/composio/tools/local/mathematical/actions/calculator.py#L29
- https://rumbling-slice-eb0.notion.site/Composio-s-Local-tools-Mathematical-has-a-code-injection-risk-in-composiohq-composio-ea0e89ee10fe4edfb9a8cfeed158c765?pvs=4
- https://vuldb.com/?ctiid.277501
- https://vuldb.com/?id.277501
- https://vuldb.com/?submit.403204
