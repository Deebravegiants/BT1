# [?] fix: preserve leading zero bytes and handle all-0xFF overflow in rich-indexer prefix search upper bound (#5166)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-04-10
Source: https://github.com/nervosnetwork/ckb/commit/5ebbc3921f392184a8f4c7dfb743159c65281c1a
Type: security-commit

## Details
fix: preserve leading zero bytes and handle all-0xFF overflow in rich-indexer prefix search upper bound (#5166)

### What problem does this PR solve?

Issue Number: close #5165

Problem Summary:

`get_binary_upper_boundary()` uses `BigUint::to_bytes_be()` which strips
leading zero bytes. For a 22-byte input like `00 01 4c bc ... 86 6e`,
the computed upper bound becomes `01 4c bc ... 86 6f` (21 bytes). Since
bytea comparison is lexicographic, the shorter result is far larger than
intended, causing prefix queries (`args >= $prefix AND args < $upper`)
to massively over-match — e.g. returning 103k scripts instead of 2.

~2.4% of mainnet scripts are affected (args starting with `0x00`),
spanning ACP locks, JoyID, CoTA, and others.

Additionally, when the input is all `0xFF` bytes, incrementing via
`BigUint` produces `[0x01, 0x00, ...]` which is lexicographically
*smaller* than `[0xFF, ...]` in bytea comparison (because `0x01 < 0xFF`
at byte 0), causing the prefix query to match **nothing**.

### What is changed and how it works?

What's Changed:

- Replaced `BigUint` with a direct lexicographic successor computation
on the byte slice using `rposition`: find the rightmost byte that is not
`u8::MAX`, increment it, then truncate everything after it. This
produces the shortest byte string that is strictly greater than every
possible extension of the input prefix, which is exactly what the range
query needs:

```rust
if let Some(i) = value.iter().rposition(|&b| b != u8::MAX) {
    let mut result = value[..=i].to_vec();
    result[i] += 1;
```

_Trimmed to 38 lines — full report: https://github.com/nervosnetwork/ckb/commit/5ebbc3921f392184a8f4c7dfb743159c65281c1a_
