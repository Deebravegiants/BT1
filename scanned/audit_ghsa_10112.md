# [M] OpenClaw: Shared-secret comparison call sites leaked length information through timing

## Summary
Severity: Medium
Advisory: GHSA-jj6q-rrrf-h66h
CVE: CVE-2026-41407
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-jj6q-rrrf-h66h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, several shared-secret comparison call sites still used early length-mismatch checks instead of the shared fixed-length comparison helper. Those paths could leak secret-length information through measurable timing differences.

## Impact

The affected paths exposed a low-severity timing side channel on secret comparison. The issue did not by itself demonstrate auth bypass, but it weakened the intended constant-time handling for shared secrets.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `be10ecef770a4654519869c3641bbb91087c8c7b` — reuse the shared secret comparison helper at affected call sites

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @kexinoh of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jj6q-rrrf-h66h
- https://nvd.nist.gov/vuln/detail/CVE-2026-41407
- https://github.com/openclaw/openclaw/commit/be10ecef770a4654519869c3641bbb91087c8c7b
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-timing-side-channel-in-shared-secret-comparison
