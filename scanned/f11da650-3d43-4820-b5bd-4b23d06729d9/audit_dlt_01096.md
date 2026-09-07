# [C] Calculation error in ark-r1cs-std

## Summary
Severity: Critical
Chain: ark-r1cs-std
Component: ark-r1cs-std
CVE: CVE-2021-38194
CWE: Incorrect Calculation
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qj3v-q2vj-4c8h
Type: github-advisory

## Details
An issue was discovered in the ark-r1cs-std crate before 0.3.1 for Rust. It does not enforce any constraints in the FieldVar::mul_by_inverse method. Thus, a prover can produce a proof that is unsound but is nonetheless verified.
