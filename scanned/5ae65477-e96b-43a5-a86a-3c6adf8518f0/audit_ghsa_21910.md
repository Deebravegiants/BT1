# [M] Go-Attestation Improper Input Validation with attacker-controlled TPM Quote

## Summary
Severity: Medium
Advisory: GHSA-99cg-575x-774p
CVE: CVE-2022-0317
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-99cg-575x-774p
Type: github-advisory

## Affected
- Go: `github.com/google/go-attestation` — affected >=0 <0.4.0

## Details
### Impact

An improper input validation vulnerability in go-attestation before 0.4.0 allows local users to provide a maliciously-formed Quote over no/some PCRs, causing `AKPublic.Verify` to succeed despite the inconsistency. Subsequent use of the same set of PCR values in `Eventlog.Verify` lacks the authentication performed by quote verification, meaning a local attacker could couple this vulnerability with a maliciously-crafted TCG log in `Eventlog.Verify` to spoof events in the TCG log, hence defeating remotely-attested measured-boot.

### Patches
This issue is resolved in version 0.4.0. If your usage of this library verifies PCRs using multiple quotes, make sure to use the new method `AKPublic.VerifyAll()` instead of `AKPublic.Verify`.

## References
- https://github.com/google/go-attestation/security/advisories/GHSA-99cg-575x-774p
- https://nvd.nist.gov/vuln/detail/CVE-2022-0317
- https://github.com/google/go-attestation/commit/82f2c9c2c76e1d3691d17ee78116d1d93a123788
- https://github.com/google/go-attestation
- https://pkg.go.dev/vuln/GO-2022-0294
