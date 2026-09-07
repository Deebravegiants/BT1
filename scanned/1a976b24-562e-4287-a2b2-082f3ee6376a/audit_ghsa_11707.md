# [M] OpenClaw: BlueBubbles Webhook Missing Rate Limiting Enables Brute-Force Password Guessing

## Summary
Severity: Medium
Advisory: GHSA-xq8g-hgh6-87hv
CVE: CVE-2026-35623
CWE: CWE-307, CWE-521
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-xq8g-hgh6-87hv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

BlueBubbles Webhook Missing Guess Rate Limiting Enables Brute-Force Guessing of Weak Webhook Password

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

BlueBubbles webhook auth previously rejected wrong passwords without throttling repeated guesses, allowing brute-force attempts against weak webhook passwords. Commit `5e08ce36d522a1c96df2bfe88e39303ae2643d92` adds repeated-guess throttling before auth failure responses.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `5e08ce36d522a1c96df2bfe88e39303ae2643d92`.

## Fix Commit(s)

- `5e08ce36d522a1c96df2bfe88e39303ae2643d92`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xq8g-hgh6-87hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35623
- https://github.com/openclaw/openclaw/commit/5e08ce36d522a1c96df2bfe88e39303ae2643d92
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-brute-force-attack-via-missing-webhook-password-rate-limiting
