# [M] n8n: NoSQL Injection in MongoDB Node Find And Replace Operation

## Summary
Severity: Medium
Advisory: GHSA-jpq7-226w-6cxx
CVE: CVE-2026-54313
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-jpq7-226w-6cxx
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.24.0

## Details
## Impact
An authenticated user with workflow edit access could supply a malicious filter value in the MongoDB node's Find And Replace operation. The value was not validated before being passed to MongoDB as a query filter, allowing unintended documents to be matched and overwritten with attacker-controlled content.

## Patches
The issue has been fixed in n8n version 2.24.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the MongoDB node by adding `n8n-nodes-base.mongoDb` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jpq7-226w-6cxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54313
- https://github.com/n8n-io/n8n
