# [C] n8n Merge Node has Arbitrary File Write leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-hv53-3329-vmrm
CVE: CVE-2026-25056
CWE: CWE-434, CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-hv53-3329-vmrm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.118.0
- npm: `n8n` — affected >=2.0.0 <2.4.0

## Details
## Impact

A vulnerability in the Merge node's SQL Query mode allowed authenticated users with permission to create or modify workflows to write arbitrary files to the n8n server's filesystem potentially leading to remote code execution.

## Patches

The issue has been fixed in n8n version 2.4.0, 1.118.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Disable or restrict use of the Merge node if not essential for operations.
- Review workflows for suspicious use of the Merge node's SQL Query mode.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## **Resources**

- [n8n Documentation — Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/) — how to globally disable specific nodes


---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility. 

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hv53-3329-vmrm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25056
- https://github.com/n8n-io/n8n
