# [H] Uptime Kuma has Persistentent User Sessions

## Summary
Severity: High
Advisory: GHSA-g9v2-wqcj-j99g
CVE: CVE-2023-44400
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-g9v2-wqcj-j99g
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=0 <1.23.3

## Details
# Summary

Attackers with access to a users' device can gain persistent account access.
This is caused by missing verification of Session Tokens after password changes and/or elapsed inactivity-periods.

# Details

`uptime-kuma` sets JWT tokens for users after successful authentication.

These tokens have the following design flaws:
- After successful login, a JWT token and it is stored in `sessionStorage` or `localStorage`. 
  Which of the two is decided based on the `Remember Me` button. 
  The users' token is valid without any time limitation, even after long periods of inactivity. 
  This increases the risk of session hijacking if, for example, a user forgets to log off and leaves the PC.
- sessions are only deleted on the client side after a user loggs out, meaning a local attacker could reuse said token with deep system access over the browser
- If a user changes a password
  - any previously logged in clients are not logged out
  - previously issued tokens remained valid forever

These flaws allow user cookies to remain valid even after changing passwords or being inactive, posing a high security risk.

# POC
### Password resets not deactivating cookies
- Log in.
- Note the user cookie.
- Change your password.
- Attempt to log in again with the same cookie.
- The cookie remains valid despite the password change.

### Inactivity not deactivating sessions
 In testing, even after a period of over a day of inactivity, the session was still valid

# Impact

Another person with local access to the device could take over the session permanently, even after hours of previous inactivity or a password change.
Such activity would not be obvious to the user (see https://github.com/louislam/uptime-kuma/issues/3481 if you want to help with this).

With this gained account access, an attacker can cause:

## confidentially loss
- monitors (including private ones not shared on public status pages)
- notification providers 
- settings like `api-keys` (only used for accessing `/metrics`)
- settings like secrets like the `Steam API Key`
- maintenance periods

## availability loss 

- by creating a lot of monitors and setting the retention policy very high leading to degraded database performance or out of storage
- by creating a lot of `HTTP(s) - Browser Engine (Chrome/Chromium) (Beta)` leading to RAM exhaustion

## integrity loss
- by the attacker deleting a monitor
- by the attacker deleting a monitor's history
- by the atacker changing the meaning of a monitor (changing where it points)

## scope creep
If operated in some restricted network, access to monitors may provide the ability to change the scope of the attack to a different piece of infrastructure, for example via SQL commands to a database server.
We have not classified this as `changed scope` because credentials stored in the application for accessing other systems are existing valid paths across the trust boundary, and the user should be aware of that.

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-g9v2-wqcj-j99g
- https://nvd.nist.gov/vuln/detail/CVE-2023-44400
- https://github.com/louislam/uptime-kuma/issues/3481
- https://github.com/louislam/uptime-kuma/commit/88afab6571ef7d4d41bb395cdb6ecd3968835a4a
- https://github.com/louislam/uptime-kuma
