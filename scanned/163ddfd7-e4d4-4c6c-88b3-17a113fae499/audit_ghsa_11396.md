# [M] OpenClaw: Chrome --no-sandbox disabled OS-level browser sandbox in sandbox browser container

## Summary
Severity: Medium
Advisory: GHSA-43x4-g22p-3hrq
CVE: CVE-2026-32046
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-43x4-g22p-3hrq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
## Summary
Sandbox browser container launched Chromium with `--no-sandbox` by default, disabling Chromium's OS-level sandbox protections.

## Affected Packages / Versions
- Package: `openclaw` (npm ecosystem)
- Latest published npm version at triage time (2026-02-21): `2026.2.19-2`
- Affected range: `<= 2026.2.19-2`
- Planned patched version for next release: `2026.2.21`

## Impact
When `--no-sandbox` is enabled by default, renderer compromise no longer requires a separate sandbox escape. This weakens container browser isolation and increases impact from renderer-side bugs.

## Resolution
- Default `--no-sandbox` removed from sandbox browser entrypoint.
- Explicit opt-in added via `OPENCLAW_BROWSER_NO_SANDBOX` / `CLAWDBOT_BROWSER_NO_SANDBOX`.
- Browser container hash migration + security audit checks added so stale containers are surfaced and can be recreated safely.

## Fix Commit(s)
- e7eba01efc4c3c400e9cfd3ce3d661cbc788a631
- 1835dec2004fe7a62c6a7ba46b8485f124ec6199

## Release Process Note
The advisory `patched_versions` field is pre-set to the planned next release (`2026.2.21`). After npm release publication, only advisory publish action should remain.

OpenClaw thanks @TerminalsandCoffee for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-43x4-g22p-3hrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32046
- https://github.com/openclaw/openclaw/commit/1835dec2004fe7a62c6a7ba46b8485f124ec6199
- https://github.com/openclaw/openclaw/commit/e7eba01efc4c3c400e9cfd3ce3d661cbc788a631
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-os-level-sandbox-bypass-via-no-sandbox-flag
