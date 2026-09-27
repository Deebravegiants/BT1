# [M] OpenClaw: Feishu Raw Card Send Surface Can Mint Legacy Card Callbacks That Bypass DM Pairing

## Summary
Severity: Medium
Advisory: GHSA-77w2-crqv-cmv3
CVE: CVE-2026-35664
CWE: CWE-288, CWE-863
Ecosystem: npm
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-77w2-crqv-cmv3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Feishu Raw card Send Surface Can Mint Legacy Card Callbacks That Bypass DM Pairing

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Feishu raw card sends could previously mint legacy callback payloads that bypassed DM pairing and let unpaired recipients reach callback handling. Commit `81c45976db532324b5a0918a70decc19520dc354` rejects legacy raw-card command payloads so callbacks stay on the normal paired path.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `81c45976db532324b5a0918a70decc19520dc354`.

## Fix Commit(s)

- `81c45976db532324b5a0918a70decc19520dc354`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-77w2-crqv-cmv3
- https://github.com/openclaw/openclaw/commit/81c45976db532324b5a0918a70decc19520dc354
- https://github.com/openclaw/openclaw
