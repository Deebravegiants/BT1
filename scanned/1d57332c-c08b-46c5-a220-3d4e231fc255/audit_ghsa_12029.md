# [H] OpenClaw's andbox browser noVNC observer lacked VNC authentication

## Summary
Severity: High
Advisory: GHSA-25gx-x37c-7pph
CVE: CVE-2026-32064
CWE: CWE-287, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-25gx-x37c-7pph
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
The sandbox browser entrypoint launched `x11vnc` without authentication (`-nopw`) for noVNC observer sessions.

OpenClaw-managed runtime flow publishes the noVNC port to host loopback only (`127.0.0.1`), so default exposure is local to the host unless operators explicitly expose the port more broadly (or run the image standalone with broad port publishing).

## Affected Packages / Versions

- Package: `docker/openclaw`
- Affected: `<= 2026.2.19-2`
- Patched: `>= 2026.2.21`

## Technical details

- `scripts/sandbox-browser-entrypoint.sh` used `x11vnc ... -nopw` for noVNC observer flow.
- `websockify` exposed noVNC for the container listener.
- OpenClaw runtime (`src/agents/sandbox/browser.ts`) already mapped host publish to loopback, but observer auth was missing.

## Fix

- Require VNC password auth in the sandbox browser entrypoint (`x11vnc -rfbauth`), replacing `-nopw`.
- Generate per-container noVNC password in runtime and inject `OPENCLAW_BROWSER_NOVNC_PASSWORD`.
- Emit short-lived noVNC observer token URLs instead of sharing raw noVNC passwords in shared URLs.
- Keep loopback-only host port publish and bump sandbox browser security hash epoch.
- Add security audit findings for sandbox browser containers that publish ports on non-loopback interfaces.

Operational note: rebuild the sandbox browser image and recreate browser containers so existing containers pick up the fix.

## Fix Commit(s)

- `621d8e1312482f122f18c43c72c67211b141da01`
- `8c1518f0f3e0533593cd2dec3a46c9b746753661`

## Release Process Note

Patched version is pre-set to the planned next release (`2026.2.21`). After npm release, this advisory can be published without further field edits.

OpenClaw thanks @TerminalsandCoffee for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-25gx-x37c-7pph
- https://nvd.nist.gov/vuln/detail/CVE-2026-32064
- https://github.com/openclaw/openclaw/commit/621d8e1312482f122f18c43c72c67211b141da01
- https://github.com/openclaw/openclaw/commit/8c1518f0f3e0533593cd2dec3a46c9b746753661
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-vnc-authentication-in-sandbox-browser-novnc-observer
