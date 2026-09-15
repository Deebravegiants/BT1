# [M] Rekor's COSE v0.0.1 entry type nil pointer dereference in Canonicalize via empty Message

## Summary
Severity: Medium
Advisory: GHSA-273p-m2cw-6833
CVE: CVE-2026-23831
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-273p-m2cw-6833
Type: github-advisory

## Affected
- Go: `github.com/sigstore/rekor` — affected >=0 <1.5.0

## Details
## Summary

Rekor’s cose v0.0.1 entry implementation can panic on attacker-controlled input when canonicalizing a proposed entry with an empty `spec.message`. `validate()` returns nil (success) when `message` is empty, leaving `sign1Msg` uninitialized, and `Canonicalize()` later dereferences `v.sign1Msg.Payload`.

## Impact

A malformed proposed entry of the `cose/v0.0.1` type can cause a panic on a thread within the Rekor process. The thread is recovered so the client receives a 500 error message and service still continues, so the availability impact of this is minimal.

## Patches

Upgrade to v1.5.0

## Workarounds

None

## References
- https://github.com/sigstore/rekor/security/advisories/GHSA-273p-m2cw-6833
- https://nvd.nist.gov/vuln/detail/CVE-2026-23831
- https://github.com/sigstore/rekor/commit/39bae3d192bce48ef4ef2cbd1788fb5770fee8cd
- https://github.com/sigstore/rekor
- https://github.com/sigstore/rekor/releases/tag/v1.5.0
