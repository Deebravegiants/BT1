# [H] Nervos CKB node panics when processing a block which parent timestamp is too new

## Summary
Severity: High
Advisory: GHSA-hjqq-29pw-96wj
Ecosystem: crates.io
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-hjqq-29pw-96wj
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0.33.0 <0.33.2
- crates.io: `ckb` — affected >=0.34.0 <0.34.1

## Details
### Impact

Adversary can initiate DOS attack by broadcasting two consecutive blocks with timestamps in the future. 

### Patches

Please upgrade to v0.34.1

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-hjqq-29pw-96wj
- https://github.com/nervosnetwork/ckb/commit/ae3c791068f2f76c67cd5483501f09de3fd8cc0b
- https://github.com/nervosnetwork/ckb/commit/c6725bb0659b6639f384d699f815117d76107388
