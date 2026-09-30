# [C] Flaw in `FieldVar::mul_by_inverse` allows unsound R1CS constraint systems

## Summary
Severity: Critical
Advisory: RUSTSEC-2021-0075
Aliases: CVE-2021-38194, GHSA-qj3v-q2vj-4c8h
Package: ark-r1cs-std
Published: 2021-07-08
Source: https://osv.dev/vulnerability/RUSTSEC-2021-0075
Type: chain-advisory

## Affected
- crates.io: `ark-r1cs-std` — affected >=0.0.0-0 <0.3.1

## Details
Versions `0.2.0` to `0.3.0` of ark-r1cs-std did not enforce any constraints in the `FieldVar::mul_by_inverse` method, allowing a malicious prover to produce an unsound proof that passes all verifier checks.
This method was used primarily in scalar multiplication for [`short_weierstrass::ProjectiveVar`](https://docs.rs/ark-r1cs-std/0.3.0/ark_r1cs_std/groups/curves/short_weierstrass/struct.ProjectiveVar.html).

This bug was fixed in commit `47ddbaa`, and was released as part of version `0.3.1` on `crates.io`.

## References
- https://crates.io/crates/ark-r1cs-std
- https://rustsec.org/advisories/RUSTSEC-2021-0075.html
- https://github.com/arkworks-rs/r1cs-std/pull/70
