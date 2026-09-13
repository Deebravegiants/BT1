# [H] libcrux has an Incorrect Check of Signer Response Norm During Verification

## Summary
Severity: High
Advisory: GHSA-cp57-fq8g-qh6v
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cp57-fq8g-qh6v
Type: github-advisory

## Affected
- crates.io: `libcrux-ml-dsa` — affected >=0 <0.0.8

## Details
The ML-DSA verification algorithm as specified in [FIPS 204, subsection 6.3](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf#subsection.6.3) requires verifiers to check that the infinity norm of the deserialized signer response $z$ does not exceed $\gamma_1 - \beta$ (line 13 of Algorithm 8). The same check is required to be performed during signature generation.

libcrux-ml-dsa did not perform this check correctly during signature verification, accepting signatures with signer response norm above the allowed maximum value. The check is correctly performed during signing.

## Impact
Applications using libcrux-ml-dsa for signature verification would have accepted signatures that would be rejected by a conforming implementation.

## Mitigation
Starting from version `0.0.8`, signature verification uses the correct value for $\gamma_1$ in the signer response norm check.

## References
- https://github.com/cryspen/libcrux/pull/1347
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0077.html
