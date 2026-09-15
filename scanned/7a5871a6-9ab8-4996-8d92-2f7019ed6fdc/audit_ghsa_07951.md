# [C] Vijkunja has Weak Password Policy Combined with Persistent Sessions After Password Change

## Summary
Severity: Critical
Advisory: GHSA-3ccg-x393-96v8
CVE: CVE-2026-27575
CWE: CWE-521, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-3ccg-x393-96v8
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
**Summary**
The application allows users to set weak passwords (e.g., 1234, password) without enforcing minimum strength requirements. Additionally, active sessions remain valid after a user changes their password.

An attacker who compromises an account (via brute-force or credential stuffing) can maintain persistent access even after the victim resets their password.


**Details**

1. Weak passwords are accepted during registration and password change.
2. No minimum length or strength validation is enforced.
3. After changing the password, previously issued session tokens remain valid.
4. No forced logout occurs across active sessions.

_Attack scenario:_

Attacker guesses or obtains weak credentials.
Logs in and obtains active session token.
Victim changes password.
Attacker continues accessing the account using the old session.

**Steps to Reproduce**

**1.** Register using a weak password (e.g., 12345678 ).
**2.** Log in and Password Change functionality.
**3.** Change account password with single character (e.g., 1 or a )
**4.** Reuse the old session.
**5.** Observe that access is still granted.

**Impact**

- Persistent account takeover
- Unauthorized access to sensitive data
- Increased brute-force success probability
- Elevated risk for administrative accounts

The combination of weak password controls and improper session invalidation significantly increases both exploitability and impact.

**Recommendation**
_**Password Policy Improvements:**_

- Enforce strong password policies – Require passwords to be 8–16+ characters with a mix of uppercase, lowercase, numbers, and special characters.
- Block common passwords – Use a blacklist of commonly used and breached passwords.
- Use secure hashing – Store passwords using strong salted hashing algorithms like bcrypt or Argon2.
- Enable account lockout – Limit failed login attempts to reduce brute-force risk.
- Educate users – Promote strong password practices and phishing awareness.

_**Session Management Fix:**_

- Invalidate all active sessions upon password change
- Revoke refresh tokens (if applicable)
- Implement token/session versioning
- Regenerate session IDs after credential updates
- Log and notify users of password change events

Implementing both controls will significantly reduce the risk of persistent account compromise.

<img width="1918" height="907" alt="Weak Password Policy Combined with Persistent Sessions After Password Change POC" src="https://github.com/user-attachments/assets/f188b69b-0472-4d2c-aeda-c145384c99ef" />

A fixed version is available at https://github.com/go-vikunja/vikunja/releases/tag/v2.0.0.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-3ccg-x393-96v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27575
- https://github.com/go-vikunja/vikunja/commit/89c17d3b23e2a23320ad135b4e8f0a14fdd91bda
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.0.0-was-released
