# [C] n8n's Improper File Access Controls Allow Arbitrary File Read by Authenticated Users

## Summary
Severity: Critical
Advisory: GHSA-gfvg-qv54-r4pc
CVE: CVE-2026-25052
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-gfvg-qv54-r4pc
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0 <2.5.0
- npm: `n8n` — affected >=0 <1.123.18

## Details
## Impact

A vulnerability in the file access controls allows authenticated users with permission to create or modify workflows to read sensitive files from the n8n host system. This can be exploited to obtain critical configuration data and user credentials, leading to complete account takeover of any user on the instance.

## Patches

The issue has been fixed in n8n version 1.123.18 and 2.5.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Restrict access to nodes that interact with the file system, particularly the "Read/Write Files from Disk" and "Git" nodes.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Resources

- [n8n Documentation — Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/) — how to globally disable specific nodes

--- 
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-gfvg-qv54-r4pc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25052
- https://github.com/n8n-io/n8n
