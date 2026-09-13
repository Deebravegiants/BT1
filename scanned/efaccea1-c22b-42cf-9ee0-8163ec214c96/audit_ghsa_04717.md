# [M] hermes-agent has an Uncontrolled Resource Consumption issue

## Summary
Severity: Medium
Advisory: GHSA-pmqc-57g8-c22c
CVE: CVE-2026-10224
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-pmqc-57g8-c22c
Type: github-advisory

## Affected
- PyPI: `hermes-agent` — affected >=0

## Details
A security vulnerability has been detected in NousResearch hermes-agent up to 2026.4.30. This vulnerability affects the function _handle_webhook_request of the file gateway/platforms/feishu.py of the component Webhook Endpoint. Such manipulation leads to resource consumption. The attack can be launched remotely. The exploit has been disclosed publicly and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10224
- https://github.com/NousResearch/hermes-agent/issues/29154
- https://github.com/NousResearch/hermes-agent/pull/73406
- https://gist.github.com/YLChen-007/0304e313d811f187ade93d3b01de0f87
- https://github.com/NousResearch/hermes-agent
- https://vuldb.com/cve/CVE-2026-10224
- https://vuldb.com/submit/822022
- https://vuldb.com/vuln/367503
- https://vuldb.com/vuln/367503/cti
