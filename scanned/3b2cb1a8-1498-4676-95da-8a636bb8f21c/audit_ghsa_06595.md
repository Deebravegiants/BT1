# [M] n8n: Custom Header Credential Values Leaked in Plaintext into LLM Node Execution Data

## Summary
Severity: Medium
Advisory: GHSA-89gh-3pgc-v5h2
CVE: CVE-2026-65589
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-89gh-3pgc-v5h2
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
Custom HTTP headers configured in credentials for certain LLM sub-nodes (including OpenAI, Anthropic, and Lemonade) are masked in the n8n UI but are written in plaintext into execution data during workflow runs. Any authenticated user with access to the execution data for an affected workflow can read the header names and values, which typically contain API keys or other secrets.

Because execution data can be persisted to the database and exported, leaked values may remain accessible beyond the lifetime of a single execution.

This issue only affects instances where workflows use LLM sub-nodes with custom headers defined in their credentials.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict access to execution data to fully trusted users only.
- Avoid configuring custom headers in LLM node credentials; use alternative authentication mechanisms where possible.
- Rotate any API keys or secrets that may have been stored as custom header values in affected credentials.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-89gh-3pgc-v5h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-65589
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-credential-exposure-via-llm-node-execution-data
