# [H] n8n Vulnerable to Arbitrary File Write on Remote Systems via SSH Node

## Summary
Severity: High
Advisory: GHSA-m82q-59gv-mcr9
CVE: CVE-2026-25055
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-m82q-59gv-mcr9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0 <2.4.0
- npm: `n8n` — affected >=0 <1.123.12

## Details
## Impact
When workflows process uploaded files and transfer them to remote servers via the SSH node without validating their metadata the vulnerability can lead to files being written to unintended locations on those remote systems potentially leading to remote code execution on those systems.

As a prerequisites an unauthenticated attacker needs knowledge of such workflows existing and the endpoints for file uploads need to be unauthenticated.

## Patches
The issue has been fixed in n8n version 2.4.0 and 1.123.12. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable or restrict access to workflows that accept file uploads via webhooks and transfer them via SSH.
- Enable webhook authentication on all endpoints that handle file uploads.
- Review usage of SSH credentials and consider rotating SSH credentials if in doubt.
These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Resources
- [n8n Documentation — Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/) — how to globally disable specific nodes

---

n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-m82q-59gv-mcr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25055
- https://github.com/n8n-io/n8n/commit/528ad6b982d0519ec170e172f57b7fdbbe175230
- https://github.com/n8n-io/n8n/commit/e0baf48c6a54808f6dbca8cb352bfa306092c223
- https://github.com/n8n-io/n8n
