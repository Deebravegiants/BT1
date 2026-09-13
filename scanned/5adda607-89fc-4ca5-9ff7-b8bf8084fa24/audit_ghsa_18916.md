# [H] Flowise does not Prevent Bypass of Password Confirmation - Unverified Password Change

## Summary
Severity: High
Advisory: GHSA-fjh6-8679-9pch
CWE: CWE-306, CWE-620
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-fjh6-8679-9pch
Type: github-advisory

## Affected
- npm: `flowise-ui` — affected >=0 <3.0.10

## Details
### Summary
Bypass of Password Confirmation - Unverified Password Change (authenticated change without current password)

An authenticated user is allowed to change their account password without supplying the current password or any additional verification. The application does not verify the actor’s authority to perform that credential change (no current-password check, no authorization enforcement). An attacker who is merely authenticated (or who can trick or coerce an authenticated session) can set a new password and gain control of the account. (ATO - Account Takeover)

### Details
Occurence - code:
https://github.com/FlowiseAI/Flowise/blob/main/packages/ui/src/views/account/index.jsx#L278 

Remote and physical scenarios can be considered.

### PoC
**Repro steps:**
1. As logged in user https://cloud.flowiseai.com/account scroll down to 'Security' section
2. Change password to the new password
3. Notice Unverified Password Change (authenticated change without current password)

**POC:** 
Password changed, and notice "Password updated" message.

**Screenshot:**
<img width="467" height="526" alt="secpw" src="https://github.com/user-attachments/assets/4cc52978-9f37-42ca-a2b2-7285c4da9f1c" />


### Impact
Full account takeover (ATO) of affected accounts (loss of confidentiality and integrity of account data).
User account recovery mechanisms (password reset flows tied to email) can be bypassed or abused if combined with this issue and the second one which I've reported (similar security issue with the email - part of credentials). (gain persistence)

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-fjh6-8679-9pch
- https://github.com/FlowiseAI/Flowise/pull/5294
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.10
