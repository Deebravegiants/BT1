# [M] n8n has SQL Injection in SeaTable Node

## Summary
Severity: Medium
Advisory: GHSA-mp4j-h6gh-f6mp
CVE: CVE-2026-42229
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-mp4j-h6gh-f6mp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
A flaw in the SeaTable node's `row:search` and `row:get` operations allowed user-controlled input to be concatenated directly into SQL query strings without escaping or parameterization. In workflows where external user input is passed via expressions into the SeaTable node's search or row retrieval parameters, an attacker could manipulate the constructed query to retrieve unintended rows from the connected SeaTable base, bypassing row-level filtering logic implemented in the workflow.

Exploitation requires a specific workflow configuration:
- The SeaTable node must be used with user-controlled input passed via expressions (e.g., from a form or webhook) into the `searchTerm` or `rowId` parameters.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the SeaTable node by adding `n8n-nodes-base.seaTable` to the `NODES_EXCLUDE` environment variable.
- Avoid passing unvalidated external user input into SeaTable node search or row retrieval parameters via expressions.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mp4j-h6gh-f6mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42229
- https://github.com/n8n-io/n8n
