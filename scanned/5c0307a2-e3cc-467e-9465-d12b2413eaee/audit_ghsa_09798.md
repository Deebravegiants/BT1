# [M] AgentScope vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-8ggf-r3vm-p3jc
CVE: CVE-2026-6605
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-8ggf-r3vm-p3jc
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A security flaw has been discovered in modelscope agentscope up to 1.0.18. This affects the function _get_bytes_from_web_url of the file src/agentscope/_utils/_common.py of the component Internal Service. Performing a manipulation results in server-side request forgery. It is possible to initiate the attack remotely. The exploit has been released to the public and may be used for attacks. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6605
- https://gist.github.com/YLChen-007/ced2d438ae79a5a11cea663c1ba2c954
- https://github.com/agentscope-ai/agentscope
- https://vuldb.com/submit/792225
- https://vuldb.com/vuln/358240
- https://vuldb.com/vuln/358240/cti
