# [M] OpenClaw's browser-origin WebSocket auth hardening gap could enable loopback password brute-force chains

## Summary
Severity: Medium
Advisory: GHSA-jmmg-jqc7-5qf4
CVE: CVE-2026-32025
CWE: CWE-287, CWE-307, CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-jmmg-jqc7-5qf4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
This issue is a browser-origin WebSocket auth chain on local loopback deployments using password auth. It is serious, but conditional: an attacker must get the user to open a malicious page and then successfully guess the gateway password.

## Context and Preconditions

OpenClaw’s web/gateway surface is designed for local use and trusted-operator workflows. In affected versions, a browser-origin client could combine three behaviors:

- Origin checks not enforced for some non-Control-UI WebSocket client IDs.
- Loopback auth attempts exempt from password-failure throttling.
- Silent local pairing path available to browser-origin non-Control-UI clients.

Successful exploitation requires all of the following:

- Gateway reachable on loopback (default).
- Password auth mode in use.
- Victim opens attacker-controlled web content.
- Password is guessable within feasible brute-force/dictionary attempts.

## Practical Impact

If the password is guessed, an attacker can establish an authenticated operator WebSocket session and invoke control-plane methods available to that role. This is not an unauthenticated internet-exposed RCE class issue by itself; it is a local browser-origin auth-hardening gap with meaningful impact under the conditions above.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<=2026.2.24` (latest published npm version as of February 26, 2026)
- Patched versions : `>=2026.2.25`

## Fix Commit(s)

- `c736f11a16d6bc27ea62a0fe40fffae4cb071fdb`

## Fix Details

- Enforce browser-origin checks for direct browser WebSocket clients beyond Control UI/Webchat (trusted-proxy forwarded flows remain supported).
- Apply browser-origin auth failure throttling with loopback exemption disabled.
- Block silent auto-pairing for non-Control-UI browser-origin clients.

## Release Process Note

`patched_versions` is pre-set to the planned next npm release (`2026.2.25`) so once that release is published, the advisory is published.

OpenClaw thanks @luz-oasis for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jmmg-jqc7-5qf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-32025
- https://github.com/openclaw/openclaw/commit/c736f11a16d6bc27ea62a0fe40fffae4cb071fdb
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-password-brute-force-via-browser-origin-websocket-authentication-bypass
