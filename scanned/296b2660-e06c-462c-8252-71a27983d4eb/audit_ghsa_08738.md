# [M] hermes-agent has a sandbox issue

## Summary
Severity: Medium
Advisory: GHSA-wm96-9gfh-vvgq
CVE: CVE-2026-9368
CWE: CWE-269, CWE-526
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-wm96-9gfh-vvgq
Type: github-advisory

## Affected
- PyPI: `hermes-agent` — affected >=0 <0.11.0

## Details
A vulnerability was identified in NousResearch hermes-agent up to 2026.4.16. This impacts the function execute_code of the file tools/code_execution_tool.py of the component Environment Variable Handler. Such manipulation leads to sandbox issue. It is possible to launch the attack remotely. The exploit is publicly available and might be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9368
- https://github.com/NousResearch/hermes-agent/commit/285bb2b9150b93445e5eded9bc897a4001b66e55
- https://gist.github.com/YLChen-007/43c72d19668421abe8ce10f299323a0a
- https://github.com/NousResearch/hermes-agent
- https://vuldb.com/submit/812229
- https://vuldb.com/vuln/365331
- https://vuldb.com/vuln/365331/cti
