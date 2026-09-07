# [H] User data in TPM attestation vulnerable to MITM

## Summary
Severity: High
Advisory: GHSA-r2h5-3hgw-8j34
CWE: CWE-200
Ecosystem: Go
Published: 2023-02-17
Source: https://github.com/advisories/GHSA-r2h5-3hgw-8j34
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/constellation/v2` — affected >=0 <2.5.2

## Details
### Impact
Attestation *user data* (such as the digest of the public key in an aTLS connection) was bound to the issuer's TPM, but not to its PCR state. An attacker could intercept a node initialization, initialize the node themselves, and then impersonate an uninitialized node to the validator. In practice, this meant that a CSP insider with sufficient privileges would have been able to join a node under their control to a Constellation cluster.

### Patches
The issue has been patched in [v2.5.2](https://github.com/edgelesssys/constellation/releases/tag/v2.5.2).

### Workarounds
none

## References
- https://github.com/edgelesssys/constellation/security/advisories/GHSA-r2h5-3hgw-8j34
- https://github.com/edgelesssys/constellation
- https://github.com/edgelesssys/constellation/releases/tag/v2.5.2
