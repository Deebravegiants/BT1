# [M] OpenClaw: Gateway hello snapshots exposed host config and state paths to non-admin clients

## Summary
Severity: Medium
Advisory: GHSA-2f7j-rp58-mr42
CVE: CVE-2026-41339
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-2f7j-rp58-mr42
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, the Gateway `connect` success snapshot exposed local `configPath` and `stateDir` metadata to non-admin clients. Low-privilege authenticated clients could learn host filesystem layout and deployment details that were not needed for their role.

## Impact

A non-admin client could recover host-specific filesystem paths and related deployment metadata, aiding host fingerprinting and chained attacks. This was an information-disclosure issue, not a direct authorization bypass.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `676b748056b5efca6f1255708e9dd9469edf5e2e` — limit connect snapshot metadata to admin-scoped clients

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @topsec-bunney for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2f7j-rp58-mr42
- https://nvd.nist.gov/vuln/detail/CVE-2026-41339
- https://github.com/openclaw/openclaw/commit/676b748056b5efca6f1255708e9dd9469edf5e2e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-information-disclosure-via-gateway-connect-snapshot
