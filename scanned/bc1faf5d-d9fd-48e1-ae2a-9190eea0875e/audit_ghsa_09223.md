# [M] n8n: Legacy ExecuteWorkflow Node Bypassed File Path Restrictions

## Summary
Severity: Medium
Advisory: GHSA-2vx9-7wpg-88jq
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-2vx9-7wpg-88jq
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.19.3

## Details
## Impact
The `ExecuteWorkflow` node's `localFile` source option read workflow files from disk without applying checks enforced by other file-reading nodes. An authenticated user with permission to create or modify workflows could supply an arbitrary file path via the REST API, bypassing the `N8N_RESTRICT_FILE_ACCESS_TO` restriction. This allowed the attacker to determine whether arbitrary files exist on the server host. Where the targeted path contained a valid workflow JSON file, the file could additionally be loaded and executed, potentially triggering actions on downstream systems connected to that workflow.

The `localFile` source option is hidden from the n8n UI since v1.2 but remains accessible via the REST API.

## Patches
The issue has been fixed in n8n version 2.20.0 or 2.19.3. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow creation and editing permissions to fully trusted users only.
- Restrict network access to the n8n REST API to trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2vx9-7wpg-88jq
- https://github.com/n8n-io/n8n
