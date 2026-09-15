# [H] Composio Eval Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-5xg7-5662-8x7j
CVE: CVE-2024-8953
CWE: CWE-627
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5xg7-5662-8x7j
Type: github-advisory

## Affected
- PyPI: `composio-core` — affected >=0 <0.5.43

## Details
In composiohq/composio version 0.4.3, the mathematical_calculator endpoint uses the unsafe eval() function to perform mathematical operations. This can lead to arbitrary code execution if untrusted input is passed to the eval() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8953
- https://github.com/ComposioHQ/composio/commit/ed82fb45dc9fbd7f07c535c72bada871c158ae5f
- https://github.com/ComposioHQ/composio-js
- https://github.com/ComposioHQ/composio/blob/b932d99e67f0fe95f8a0a24be9352e3f99059bc3/python/composio/tools/local/mathematical/actions/calculator.py#L37
- https://huntr.com/bounties/8203d721-e05f-4500-a5bc-c0bec980420c
