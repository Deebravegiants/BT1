# [M] OpenClaw: Telegram DM-Scoped Inline Button Callbacks Bypass DM Pairing and Mutate Session State

## Summary
Severity: Medium
Advisory: GHSA-j4c9-w69r-cw33
CVE: CVE-2026-35661
CWE: CWE-285, CWE-288, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-j4c9-w69r-cw33
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Telegram DM-Scoped Inline Button Callbacks Bypass DM Pairing and Mutate Session State

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Telegram callback queries from direct messages previously used weaker callback-only authorization and could mutate session state without satisfying normal DM pairing. Commit `269282ac69ab6030d5f30d04822668f607f13065` enforces DM authorization for callbacks.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `269282ac69ab6030d5f30d04822668f607f13065`.

## Fix Commit(s)

- `269282ac69ab6030d5f30d04822668f607f13065`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j4c9-w69r-cw33
- https://nvd.nist.gov/vuln/detail/CVE-2026-35661
- https://github.com/openclaw/openclaw/commit/269282ac69ab6030d5f30d04822668f607f13065
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-telegram-dm-scoped-inline-button-callback-authorization-bypass
