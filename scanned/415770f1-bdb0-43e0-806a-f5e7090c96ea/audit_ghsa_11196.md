# [M] OpenClaw Loopback CDP probe can leak Gateway token to local listener

## Summary
Severity: Medium
Advisory: GHSA-v3j7-34xh-6g3w
CVE: CVE-2026-22174
CWE: CWE-290, CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-v3j7-34xh-6g3w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
A local process can capture the OpenClaw Gateway auth token from Chrome CDP probe traffic on loopback.

### Details
Affected versions inject `x-openclaw-relay-token` for loopback CDP URLs, and CDP reachability probes send that header to `/json/version`.
If an attacker controls the probed loopback port, they can read that token and reuse it as Gateway bearer auth.

Relevant code paths (pre-fix):
- `src/browser/extension-relay.ts` (`getChromeExtensionRelayAuthHeaders`)
- `src/browser/cdp.helpers.ts` (`getHeadersWithAuth`)
- `src/browser/chrome.ts` (`fetchChromeVersion`)

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published (at triage): `2026.2.21-2`
- Vulnerable: `<= 2026.2.21-2`
- Patched: >= 2026.2.22

### Deployment Model Applicability
This does **not** change OpenClaw’s documented security model for standard single-owner installs (you own the machine/VPS and trust local processes under that OS account boundary).
Risk is for **non-standard shared-user/shared-host installs** where an untrusted local user/process can race/bind the loopback relay port.

### Impact
- Local credential disclosure.
- Follow-on impact depends on local deployment and enabled Gateway capabilities.

### Fix Commit(s)
- `afa22acc4a09fdf32be8a167ae216bee85c30dad`

### Release Process Note
Patched version is set to >= 2026.2.22 for the published release.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v3j7-34xh-6g3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-22174
- https://github.com/openclaw/openclaw/commit/afa22acc4a09fdf32be8a167ae216bee85c30dad
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-gateway-token-disclosure-via-chrome-cdp-probe
