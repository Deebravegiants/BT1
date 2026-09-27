# [M] RustDesk Auth Proof Uses Server-Controlled Salt/Challenge and Fast Double-SHA256, Enabling Offline Brute-Force

## Summary
Severity: Medium
Advisory: CVE-2026-30789
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30789
Type: osv

## Details
Use of Password Hash With Insufficient Computational Effort, Improper Restriction of Excessive Authentication Attempts vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android (Client login, peer authentication modules) allows Password Brute Forcing.

The authentication proof is SHA256(SHA256(password + salt) + challenge), where both the salt and the challenge are generated entirely by the server with no client-side nonce, and the hash uses no slow key-derivation function. A rogue or on-path API/relay server (see CVE-2026-30794 / CVE-2026-30797) can issue a chosen salt and challenge, capture the resulting proof, and recover the password offline. The capture-replay claim (CWE-294) is withdrawn: the challenge is regenerated per connection (challenge = Config::get_auto_password(6)), so a captured proof is not replayable against the legitimate server. The 1.4.7 OTP brute-force limiter and the existing LOGIN_FAILURES counter constrain only ONLINE attempts and do not address offline recovery.

This vulnerability is associated with program files src/client.rs and program routines handle_hash(), handle_login_from_ui() (login proof construction).

This issue affects RustDesk Client: through 1.4.8.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30789.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30789
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://rustdesk.com/docs/en/client/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
