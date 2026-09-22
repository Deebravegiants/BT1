# [C] n8n has OS Command Injection in Git Node

## Summary
Severity: Critical
Advisory: GHSA-9g95-qf3f-ggrw
CVE: CVE-2026-25053
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-9g95-qf3f-ggrw
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0 <2.5.0
- npm: `n8n` — affected >=0 <1.123.10

## Details
## Impact

Vulnerabilities in the Git node allowed authenticated users with permission to create or modify workflows to execute arbitrary system commands or read arbitrary files on the n8n host.

## Patches

The issue has been fixed in n8n versions 2.5.0, and 1.123.10. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Restrict or disable access to the Git node if not essential for operations.
- Deploy n8n in a hardened environment with restricted operating system privileges and network access to reduce the impact of potential exploitation.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Resources

- [n8n Documentation — Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/) — how to globally disable specific nodes

--- 

n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9g95-qf3f-ggrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25053
- https://github.com/n8n-io/n8n
