# [C] n8n Has Expression Escape Vulnerability Leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-6cqr-8cfr-67f8
CVE: CVE-2026-25049
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-6cqr-8cfr-67f8
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.17
- npm: `n8n` — affected >=2.0.0 <2.5.2

## Details
### Impact

Additional exploits in the expression evaluation of n8n have been identified and patched following [CVE-2025-68613](https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp).

An authenticated user with permission to create or modify workflows could abuse crafted expressions in workflow parameters to trigger unintended system command execution on the host running n8n.

### Patches

The issue has been fixed in n8n versions 1.123.17 and 2.5.2. Users should upgrade to these versions or later to remediate the vulnerability.

### Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Deploy n8n in a hardened environment with restricted operating system privileges and network access to reduce the impact of potential exploitation.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

### Resources

- Best practices for [securing n8n](https://docs.n8n.io/hosting/securing/overview/)
- Initial vulnerability advisory: [CVE-2025-68613](https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp)

---

n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-6cqr-8cfr-67f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25049
- https://github.com/n8n-io/n8n/commit/7860896909b3d42993a36297f053d2b0e633235d
- https://github.com/n8n-io/n8n/commit/936c06cfc1ad269a89e8ef7f8ac79c104436d54b
- https://github.com/n8n-io/n8n
