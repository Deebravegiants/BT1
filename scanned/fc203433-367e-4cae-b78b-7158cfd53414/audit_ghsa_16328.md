# [H] Nervos CKB Panic on malformed input

## Summary
Severity: High
Advisory: GHSA-wjxc-pjx9-4wvm
Ecosystem: crates.io
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-wjxc-pjx9-4wvm
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.34.2

## Details
### Impact
CKB process will panic when received malformed p2p message because of snappy, which is used to compress network messages

### References
https://github.com/BurntSushi/rust-snappy/issues/29

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-wjxc-pjx9-4wvm
