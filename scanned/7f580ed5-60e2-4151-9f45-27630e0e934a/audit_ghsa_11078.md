# [M] OpenClaw: Synology Chat Webhook Pre-Auth Rate-Limit Bypass Enables Brute-Force Guessing of Webhook Token

## Summary
Severity: Medium
Advisory: GHSA-mf5g-6r6f-ghhm
CVE: CVE-2026-35646
CWE: CWE-307, CWE-521
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-mf5g-6r6f-ghhm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Synology Chat Webhook Pre-Auth Rate-Limit Bypass Enables Brute-Force Guessing of Weak Webhook Token

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Synology Chat webhook auth previously rejected invalid tokens without throttling repeated guesses, allowing brute-force attempts against weak webhook secrets. Commit `0b4d07337467f4d40a0cc1ced83d45ceaec0863c` adds repeated-guess throttling before auth failure responses.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `0b4d07337467f4d40a0cc1ced83d45ceaec0863c`.

## Fix Commit(s)

- `0b4d07337467f4d40a0cc1ced83d45ceaec0863c`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mf5g-6r6f-ghhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-35646
- https://github.com/openclaw/openclaw/commit/0b4d07337467f4d40a0cc1ced83d45ceaec0863c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-pre-authentication-rate-limit-bypass-in-webhook-token-validation
