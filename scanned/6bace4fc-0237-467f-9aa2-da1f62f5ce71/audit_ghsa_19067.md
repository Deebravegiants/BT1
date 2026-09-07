# [H] OneUptime Unauthorized User Creation via API

## Summary
Severity: High
Advisory: GHSA-m449-vh5f-574g
CVE: CVE-2025-65966
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-m449-vh5f-574g
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <9.1.0

## Details
### Summary
A low-permission user can create new accounts through a direct API request instead of being restricted to the intended interface.

### PoC
A low-permission user sends a crafted API request to the user-creation endpoint and the system creates the account successfully.
![WhatsApp Image 2025-11-23 at 14 27 32_0e0f5889](https://github.com/user-attachments/assets/5a539310-c9a2-4466-8926-b49b9b2a2422)

### Impact
This allows attackers to create unauthorized accounts.

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-m449-vh5f-574g
- https://nvd.nist.gov/vuln/detail/CVE-2025-65966
- https://github.com/OneUptime/oneuptime/commit/07bc6d4edde7397ea6b88f889c065ec392052ab4
- https://github.com/OneUptime/oneuptime
