# [M] CVE-2026-7658

## Summary
Severity: Medium
Advisory: CVE-2026-7658
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-7658
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 does not properly validate the username field, allowing attackers to inject path traversal sequences and bypass containment checks. This enables multiple severe impacts, including arbitrary directory deletion, cross-tenant data destruction, and JWT signing key deletion leading to session invalidation.

## References
- https://www.ibm.com/support/pages/node/7282647
