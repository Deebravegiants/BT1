# [C] n8n: HTTP Request Node Pagination Prototype Pollution to RCE

## Summary
Severity: Critical
Advisory: GHSA-c8xv-5998-g76h
CVE: CVE-2026-44789
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-c8xv-5998-g76h
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.43
- npm: `n8n` — affected >=2.21.0 <2.22.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.20.7

## Details
## Impact
An authenticated user with permission to create or modify workflows could achieve global prototype pollution via an unvalidated pagination parameter in the HTTP Request node. Combined with other techniques this could lead to RCE on the instance.

## Patches
The issue has been fixed in n8n versions 1.123.43, 2.20.7, and 2.22.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the HTTP Request node by adding `n8n-nodes-base.httpRequest` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-c8xv-5998-g76h
- https://nvd.nist.gov/vuln/detail/CVE-2026-44789
- https://github.com/n8n-io/n8n
