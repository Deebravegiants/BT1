# [M] Blst has logical error in SigValidate in Go bindings

## Summary
Severity: Medium
Advisory: GHSA-8c37-7qx3-4c4p
Ecosystem: Go
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-8c37-7qx3-4c4p
Type: github-advisory

## Affected
- Go: `github.com/supranational/blst` — affected >=0.3.0 <0.3.11

## Details
### Impact

Blst versions v0.3.0 through 0.3.10 failed to perform a signature group-check if the call to `SigValidate` in the Go bindings was complemented with a check for infinity. Formally speaking, infinity, or the identity element of the elliptic curve group, is a member of the group, and the group-check should allow it. An initial review of blst users on GitHub did not uncover any use of this function with the complementary infinity check. This optional check was added as a convenience feature because despite infinity being a legitimate member of the group, individual signatures should never be infinite (as it is equivalent to having zero for the secret key), and observing one should raise a flag. 

### Description

The vulnerable function is declared as `SigValidate(sigInfcheck bool) bool` and if called with `sigInfcheck` argument set to `true`, the group-check was omitted. The group-check is required to be performed on untrusted input, because the pairing, the corner-stone operation of the signature scheme, is defined only on points that are members of a specific cyclic group, which is a subset of all the possible points on elliptic curves in question. Submitting an untrusted point outside the group opens up the possibility of accepting an alternative signature for a chosen message.

It should be noted that the SigValidate call is not the only way to perform the group-checks. There are optional checks integrated into various other verification methods, such as `Verify`, `AggregateVerify`, etc., as well as signature aggregation methods, such as `PairingAggregate*`. The reason why there are multiple options is that the group-check is a relatively expensive operation, and application developers are arguably entitled the freedom to choose when it's performed.

### Patches

This issue has been resolved in the v0.3.11 release and users are advised to update if their application is affected or alternatively omit the complementary infinity check.

### Credits

A special thanks to Yunjong Jeong (@blukat29) for the discovery and disclosure of this vulnerability.

## References
- https://github.com/supranational/blst/security/advisories/GHSA-8c37-7qx3-4c4p
- https://github.com/supranational/blst/commit/fb91221c91c82f65bfc7f243256308977a06d48b
- https://github.com/supranational/blst
- https://github.com/supranational/blst/releases/tag/v0.3.11
