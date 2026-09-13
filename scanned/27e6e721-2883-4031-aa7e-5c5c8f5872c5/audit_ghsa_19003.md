# [H] Flowise Fails to Invalidate Existing Sessions After Password Changes

## Summary
Severity: High
Advisory: GHSA-x7rp-qj2h-ghgw
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-x7rp-qj2h-ghgw
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.10

## Details
### Summary
Failure to Invalidate Existing Sessions After Password Change (Persistent Session / Session Invalidity Failure).

### Details
After a user changes their password, the application does not invalidate other active sessions or session tokens that were established before the change. An attacker who already has an active session (e.g., via a stolen session token, device left logged in, or other access) continues to be authenticated even after the legitimate user rotates credentials, allowing the attacker to retain access despite the user’s password change.

### PoC
**Repro steps:**
1. As logged in user on two browsers (ie. Chrome and Firefox, with incognito/private mode) https://cloud.flowiseai.com/account change password, on the Chrome for example
2. Refresh the site on Firefox (second browser) - notice that still logged in (despite credentials were changed)

**POC:**
Steps described above (in Repro steps) completed successfully.

### Impact
Persistent unauthorized access despite credential rotation - undermines the primary purpose of password changes as a remediation step.
Enables attackers with an active session (remote or physical access to a device) to continue acting as the user (confidentiality and integrity impact).
If session tokens are not bound to the credential state, forced password changes won’t terminate attacker sessions.

**Resources**
OWASP Session Management Cheat Sheet
CWE-613: Insufficient Session Expiration

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x7rp-qj2h-ghgw
- https://github.com/FlowiseAI/Flowise/pull/5294
- https://github.com/FlowiseAI/Flowise
