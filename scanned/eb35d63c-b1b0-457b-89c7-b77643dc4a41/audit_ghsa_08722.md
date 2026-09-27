# [H] SillyTavern: Existing sessions are not invalidated after password change, allowing session reuse and account takeover

## Summary
Severity: High
Advisory: GHSA-wmm3-h9qj-p5v6
CVE: CVE-2026-44648
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-wmm3-h9qj-p5v6
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
### Summary
Changing a user’s password does not invalidate existing sessions, allowing an attacker with a stolen cookie to retain access even after the victim resets their password.

### Details
SillyTavern relies on cookie-session for authentication, storing all session data (user handle, permissions) in a signed cookie. The endpoints POST /api/users/change-password and POST /api/users/recover-step2 only update the password hash in the database but do not expire current sessions. Because the session is stateless and stored entirely in the client cookie, there is no server-side mechanism to revoke a token once issued.

### PoC
1.Log into the same SillyTavern account from two different browsers (e.g., Chrome and Firefox private mode).
2.In Chrome, change the account password under User Settings → Change Password.
3.In Firefox, refresh the page or perform a protected action (e.g., view API keys).
4.Expected: Firefox session should be invalidated and ask for login.
5.Actual: Firefox remains fully authenticated, able to perform all actions as the targeted user.

### Impact
An attacker who obtains a valid session cookie (via XSS, MITM, physical access, etc.) can continue using it indefinitely, even after the legitimate user changes their password.
This nullifies the most common recovery measure against session theft.
The default cookie lifespan is 400 days, giving an attacker a very long exploitation window.

### Resolution
A fix was released in the version 1.18.0, invalidating a session cookie on account password change.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-wmm3-h9qj-p5v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44648
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.18.0
