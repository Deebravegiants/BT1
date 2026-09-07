# [H] libcrux: Panic in Signature Hint Decoding During Verification

## Summary
Severity: High
Advisory: GHSA-xrf2-5r3p-5wgj
CWE: CWE-125, CWE-1285
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-xrf2-5r3p-5wgj
Type: github-advisory

## Affected
- crates.io: `libcrux-ml-dsa` — affected >=0 <0.0.8

## Details
During ML-DSA verification the serialized hint values are decoded as specified in algorithm 22 `HintBitUnpack` of [FIPS 204, subsection 7.1](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf#%5B%7B%22num%22%3A120%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22FitH%22%7D%2C657%5D). The algorithm requires that the cumulative hint counters per row of the hint vector are strictly increasing and below a maximum value which depends on the choice of ML-DSA parameter set (line 4).

In libcrux-ml-dsa, hint decoding did not check the boundedness of the cumulative hint counter of the last row of the hint vector.

## Impact
A manipulated invalid hint can cause an out-of-bounds memory access since the hint decoding logic may attempt to read outside the bounds of the serialized signature, causing a runtime panic.

## Mitigation
Starting from version `0.0.8`, hint decoding will check the cumulative hint counter of the last row as well.

## References
- https://github.com/cryspen/libcrux/pull/1348
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0076.html
