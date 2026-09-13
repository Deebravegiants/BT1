# [H] Striae has a hash validation utility vulnerability

## Summary
Severity: High
Advisory: GHSA-mmf8-487q-p45m
CVE: CVE-2026-31839
CWE: CWE-327, CWE-353, CWE-354
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-mmf8-487q-p45m
Type: github-advisory

## Affected
- npm: `@striae-org/striae` — affected >=0.9.22-0 <3.0.0

## Details
## Summary

A high-severity integrity bypass vulnerability existed in Striae's digital confirmation workflow prior to v3.0.0. Hash-only validation trusted manifest hash fields that could be modified together with package content, allowing tampered confirmation packages to pass integrity checks.

## Impact

Confirmation package integrity could be bypassed because both content and hash values were mutable in the same trust boundary. An attacker with access to an exported package could alter confirmation data and recompute hashes so hash-only checks still passed.

This affects users relying on digital confirmations as an immutability and forensic chain-of-custody control.

## Patches

Patched in **v3.0.0**.

Upgrade to:
- `v3.0.0` or later

Security behavior added in v3.0.0:
- Server-issued asymmetric signatures for forensic manifests
- Canonical payload signature verification during import and manual hash verification
- Fail-closed behavior when signature metadata is missing or invalid
- Signature/key provenance support for audit-related workflows

## Workarounds

There is no full cryptographic workaround equivalent to upgrading.

Temporary mitigations:
- Treat hash-only validation as a tamper indicator, not proof of immutability
- Restrict package exchange to trusted authenticated internal channels
- Require out-of-band reviewer attestation for sensitive confirmation workflows
- Pause imports from untrusted sources until upgraded

## References
- https://github.com/striae-org/striae/security/advisories/GHSA-mmf8-487q-p45m
- https://nvd.nist.gov/vuln/detail/CVE-2026-31839
- https://github.com/striae-org/striae
- https://github.com/striae-org/striae/releases/tag/v3.0.0
