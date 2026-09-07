# [M] OpenClaw: Telegram Webhook Missing Guess Rate Limiting Enables Brute-Force Guessing of Weak Webhook Secret

## Summary
Severity: Medium
Advisory: GHSA-vcx4-4qxg-mfp4
CVE: CVE-2026-35628
CWE: CWE-307, CWE-521
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vcx4-4qxg-mfp4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Telegram Webhook Missing Guess Rate Limiting Enables Brute-Force Guessing of Weak Webhook Secret

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Telegram webhook auth previously rejected bad secrets but did not throttle repeated guesses, allowing brute-force attempts against weak webhook secrets. Commit `c2c136ae9517ddd0789d742a0fdf4c10e8c729a7` adds repeated-guess throttling before auth failure responses.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `c2c136ae9517ddd0789d742a0fdf4c10e8c729a7`.

## Fix Commit(s)

- `c2c136ae9517ddd0789d742a0fdf4c10e8c729a7`

## Release Process Note

`2026.3.25` is the next planned OpenClaw release version in `package.json`. This advisory is being published ahead of that npm release so the draft is no longer blocked; once `2026.3.25` is published, the structured patched-version metadata will match the released artifact.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vcx4-4qxg-mfp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-35628
- https://github.com/openclaw/openclaw/commit/c2c136ae9517ddd0789d742a0fdf4c10e8c729a7
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-brute-force-attack-via-missing-telegram-webhook-rate-limiting
