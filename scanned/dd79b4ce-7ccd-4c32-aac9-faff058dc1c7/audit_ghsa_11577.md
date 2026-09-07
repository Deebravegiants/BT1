# [M] OpenClaw session transcript files were created without forced user-only permissions

## Summary
Severity: Medium
Advisory: GHSA-vr7j-g7jv-h5mp
CVE: CVE-2026-33572
CWE: CWE-276, CWE-732
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-vr7j-g7jv-h5mp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.17

## Details
`openclaw` created new session transcript JSONL files with overly broad default permissions in affected releases. On multi-user hosts, other local users or processes could read transcript contents, including secrets that might appear in tool output.

## Affected Packages / Versions

- Package: `openclaw` (`npm`)
- Affected versions: `<= 2026.2.15`
- First fixed version: `2026.2.17`
- Current latest npm release checked during verification: `2026.3.13` (not affected)

## Impact

Session transcript JSONL files are created under the local OpenClaw session store. In affected releases, newly created transcript files did not force user-only permissions, so transcript contents could be readable by other local users depending on the host environment and umask behavior.

## Fix

New transcript files are now created with `0o600` permissions. Existing transcript permission drift is also remediated by the security audit fix flow.

Verified in code:

- `src/config/sessions/transcript.ts:82` writes new transcript files with `mode: 0o600`
- `src/config/sessions/sessions.test.ts:303` includes regression coverage asserting `0o600`

## Fix Commit(s)

- `095d522099653367e1b76fa5bb09d4ddf7c8a57c`

## Release Note

This fix first shipped in `2026.2.17` and is present in the current npm release `2026.3.13`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vr7j-g7jv-h5mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33572
- https://github.com/openclaw/openclaw/commit/095d522099653367e1b76fa5bb09d4ddf7c8a57c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insufficient-file-permissions-in-session-transcript-files
