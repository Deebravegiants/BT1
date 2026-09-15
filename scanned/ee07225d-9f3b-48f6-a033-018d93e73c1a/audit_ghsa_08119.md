# [H] OpenClaw: Prevent shell injection in macOS keychain credential write

## Summary
Severity: High
Advisory: GHSA-4564-pvr2-qq4h
CVE: CVE-2026-27487
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-4564-pvr2-qq4h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary
On macOS, the Claude CLI keychain credential refresh path constructed a shell command to write the updated JSON blob into Keychain via `security add-generic-password -w ...`. Because OAuth tokens are user-controlled data, this created an OS command injection risk.

The fix avoids invoking a shell by using `execFileSync("security", argv)` and passing the updated keychain payload as a literal argument.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Platform: macOS only
- Affected versions: `<= 2026.2.13`

## Fix
- Patched version: `>= 2026.2.14` (next release)
- Fix PR: #15924
- Fix commits (merged to `main`):
  - `9dce3d8bf83f13c067bc3c32291643d2f1f10a06`
  - `66d7178f2d6f9d60abad35797f97f3e61389b70c`
  - `b908388245764fb3586859f44d1dff5372b19caf`

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4564-pvr2-qq4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-27487
- https://github.com/openclaw/openclaw/pull/15924
- https://github.com/openclaw/openclaw/commit/66d7178f2d6f9d60abad35797f97f3e61389b70c
- https://github.com/openclaw/openclaw/commit/9dce3d8bf83f13c067bc3c32291643d2f1f10a06
- https://github.com/openclaw/openclaw/commit/b908388245764fb3586859f44d1dff5372b19caf
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
