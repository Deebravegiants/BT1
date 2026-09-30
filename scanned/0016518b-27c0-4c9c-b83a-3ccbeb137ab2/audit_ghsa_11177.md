# [M] OpenClaw: Feishu webhook reads and parses unauthenticated request bodies before signature validation

## Summary
Severity: Medium
Advisory: GHSA-3h52-cx59-c456
CVE: CVE-2026-35640
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-3h52-cx59-c456
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Feishu webhook reads and parses unauthenticated request bodies before signature validation

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Feishu webhook handling previously parsed JSON before signature validation, which let unauthenticated callers force full JSON parsing work before rejection. Commit `5e8cb22176e9235e224be0bc530699261eb60e53` reads the raw request body, validates the signature first, and only then parses JSON.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `5e8cb22176e9235e224be0bc530699261eb60e53`.

## Fix Commit(s)

- `5e8cb22176e9235e224be0bc530699261eb60e53`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3h52-cx59-c456
- https://nvd.nist.gov/vuln/detail/CVE-2026-35640
- https://github.com/openclaw/openclaw/commit/5e8cb22176e9235e224be0bc530699261eb60e53
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-unauthenticated-webhook-request-parsing
