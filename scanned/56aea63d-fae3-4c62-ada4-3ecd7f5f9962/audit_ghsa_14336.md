# [M] Parsing borsh messages with ZST which are not-copy/clone is unsound

## Summary
Severity: Medium
Advisory: GHSA-fjx5-qpf4-xjf2
Ecosystem: crates.io
Published: 2023-04-17
Source: https://github.com/advisories/GHSA-fjx5-qpf4-xjf2
Type: github-advisory

## Affected
- crates.io: `borsh` — affected >=0 <1.0.0-alpha.1

## Details
Affected versions of borsh cause undefined behavior when zero-sized-types (ZST) are parsed and the Copy/Clone traits are not implemented/derived. For instance if 1000 instances of a ZST are deserialized, and the ZST is not copy (this can be achieved through a singleton), then accessing/writing to deserialized data will cause a segmentation fault.

There is currently no way for borsh to read data without also providing a Rust type. Therefore, if you are not using ZST for serialization, then you are not affected by this issue.

## References
- https://github.com/near/borsh-rs/issues/19
- https://github.com/near/borsh-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0033.html
