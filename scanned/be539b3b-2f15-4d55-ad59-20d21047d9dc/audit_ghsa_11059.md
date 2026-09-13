# [C] n8n: Prototype Pollution in XML and GSuiteAdmin node parameters lead to RCE

## Summary
Severity: Critical
Advisory: GHSA-mxrg-77hm-89hv
CVE: CVE-2026-33696
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-mxrg-77hm-89hv
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3
- npm: `n8n` — affected >=0 <1.123.27

## Details
## Impact
An authenticated user with permission to create or modify workflows could exploit a prototype pollution vulnerability in the GSuiteAdmin node. By supplying a crafted parameter as part of node configuration, an attacker could write attacker-controlled values onto `Object.prototype`. An attacker could use this prototype pollution to achieve remote code execution on the n8n instance.

## Patches
The issue has been fixed in n8n versions 2.14.1, 2.13.3, and 1.123.27. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the XML node by adding `n8n-nodes-base.xml` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mxrg-77hm-89hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33696
- https://github.com/n8n-io/n8n
