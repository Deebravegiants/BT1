# [H] Reading on uninitialized memory may cause UB ( `util::read_spv()` )

## Summary
Severity: High
Advisory: GHSA-qj69-c89v-jwq2
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-qj69-c89v-jwq2
Type: github-advisory

## Affected
- crates.io: `ash` — affected >=0 <0.33.1

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation.

Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/MaikKlein/ash/issues/354
- https://github.com/MaikKlein/ash
- https://rustsec.org/advisories/RUSTSEC-2021-0090.html
