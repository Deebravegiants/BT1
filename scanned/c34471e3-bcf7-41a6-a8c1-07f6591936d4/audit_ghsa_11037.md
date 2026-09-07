# [H] OpenClaw: Node reconnect metadata spoofing could bypass platform-based node command policy

## Summary
Severity: High
Advisory: GHSA-r65x-2hqr-j5hf
CVE: CVE-2026-32014
CWE: CWE-290, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-r65x-2hqr-j5hf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
## Summary

A paired node device could reconnect with spoofed `platform`/`deviceFamily` metadata and broaden node command policy eligibility because reconnect metadata was accepted from the client while these fields were not bound into the device-auth signature.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.25`
- Latest published version at update time: `2026.2.25`
- Patched version (pre-set for next release): `2026.2.26`

## Impact

In configurations where node command policy differs by platform, an attacker with an already paired node identity on the trusted network could spoof reconnect metadata and gain access to commands that should remain blocked for the originally paired platform.

## Fix

- Add device-auth payload `v3` that signs normalized `platform` and `deviceFamily`.
- Verify `v3` first (fallback to `v2` for compatibility), while pinning paired metadata server-side.
- Reject reconnect metadata mismatches and require explicit repair pairing to change pinned metadata.
- Add regression coverage for reconnect spoof attempts.

## Fix Commit(s)

- `7d8aeaaf06e2e616545d2c2cec7fa27f36b59b6a`

## Release Process Note

`patched_versions` is pre-set to the planned next release `2026.2.26`; once that npm release is published, the advisory can be published without further field edits.

OpenClaw thanks @76embiid21 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r65x-2hqr-j5hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-32014
- https://github.com/openclaw/openclaw/commit/7d8aeaaf06e2e616545d2c2cec7fa27f36b59b6a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-node-reconnect-metadata-spoofing-via-unsigned-platform-fields
