# [H] Go-Attestation: Hash injection into trusted measurement list via unskipped SignatureHeaderSize vendor bytes in parseEfiSignatureList()

## Summary
Severity: High
Advisory: GHSA-9r4w-jg96-92mv
CVE: CVE-2026-12681
CWE: CWE-20, CWE-1285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-9r4w-jg96-92mv
Type: github-advisory

## Affected
- Go: `github.com/google/go-attestation` — affected >=0 <0.6.1

## Details
## Summary

`parseEfiSignatureList()` in `attest/internal/events.go` does not skip
`SignatureHeaderSize` vendor bytes before reading `EFI_SIGNATURE_LIST`
signature entries, violating UEFI specification section 31.4.1.

## Impact

For `hashSHA256SigGUID` lists, attacker-controlled vendor header bytes are appended directly to the trusted SHA256 hash list. A crafted TPM event log can inject arbitrary SHA256 hashes into the verifier's trusted measurement database, allowing a remote attestation verifier to accept a compromised boot state as legitimate — breaking the core integrity guarantee of remote attestation.

## Root Cause

After `binary.Read(&signatures.Header)` reads 28 bytes, `buf` points to the start of the `SignatureHeaderSize` vendor bytes. Both entry loops start at `sigOffset := 0` instead of `sigOffset := SignatureHeaderSize`, causing vendor bytes to be read as signature entries.

## Affected versions

All versions through commit `f877374` (2026-05-15).

## Fix

Pull request: https://github.com/google/go-attestation/pull/502

- Add bound check: `SignatureHeaderSize` must not exceed remaining list space
- Skip `SignatureHeaderSize` bytes before both entry loops
- Regression test: `TestParseEfiSignatureListNonZeroSignatureHeaderSize`

## References
- https://github.com/google/go-attestation/security/advisories/GHSA-9r4w-jg96-92mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-12681
- https://github.com/google/go-attestation/pull/502
- https://github.com/google/go-attestation/commit/b6e905e7ae52937f02b5ca494dd1c6a3ac7a1003
- https://github.com/google/go-attestation
- https://github.com/google/go-attestation/releases/tag/v0.6.1
