# [M] mz-avro's incorrect use of `set_len` allows for un-initialized memory

## Summary
Severity: Medium
Advisory: GHSA-jwh2-vrr9-vcp2
Ecosystem: crates.io
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-jwh2-vrr9-vcp2
Type: github-advisory

## Affected
- crates.io: `mz-avro` — affected >=0 <0.7.0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` 
implementation.

Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure)
and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke
undefined behavior.

Note: there is only UB in the case where a user provides a struct whose `Read`
implementation inspects the buffer passed to `read_exact` before writing to it.
This is an unidiomatic (albeit possible) `Read` implementation.

See https://github.com/MaterializeInc/materialize/issues/8669 for details.

## References
- https://github.com/MaterializeInc/materialize/issues/8669
- https://github.com/MaterializeInc/materialize
- https://rustsec.org/advisories/RUSTSEC-2021-0138.html
