# [H] n8n Has a Source Control Pull SQL Injection

## Summary
Severity: High
Advisory: GHSA-mhrx-qhrj-673w
CVE: CVE-2026-44792
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-mhrx-qhrj-673w
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.43
- npm: `n8n` — affected >=2.21.0 <2.21.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.20.7

## Details
## Impact
An attacker with write access to the git repository connected to an n8n Source Control configuration could commit a malicious Data Table JSON file containing a crafted column name. When an administrator performed a Source Control Pull, n8n imported the file and could lead to SQL injection on the internal PostgreSQL instance.

Exploitation requires all of the following conditions:
- The n8n instance uses PostgreSQL as its database backend.
- The Source Control feature is enabled and connected to a repository the attacker can write to.
- An administrator triggers a Source Control Pull.

## Patches
The issue has been fixed in n8n version 1.123.43, 2.20.7, and 2.21.1. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the Source Control feature if it is not actively required.
- Restrict write access to the connected git repository to fully trusted users only.
- Avoid pulling from repositories that may have been modified by untrusted parties.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mhrx-qhrj-673w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44792
- https://github.com/n8n-io/n8n
