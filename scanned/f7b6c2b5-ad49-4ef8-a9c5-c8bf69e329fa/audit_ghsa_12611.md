# [M] cyfs-base vulnerable to misaligned pointer dereference in `ChunkId::new`

## Summary
Severity: Medium
Advisory: GHSA-g753-ghr7-q33w
Ecosystem: crates.io
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-g753-ghr7-q33w
Type: github-advisory

## Affected
- crates.io: `cyfs-base` — affected >=0

## Details
The function `ChunkId::new` creates a misaligned pointer by casting mutable pointer of `u8` slice which has alignment 1 to the mutable pointer of `u32` which has alignment 4, and dereference the misaligned pointer leading UB, which should not be allowed in safe function.

## References
- https://github.com/buckyos/CYFS/issues/275
- https://github.com/buckyos/CYFS/commit/e030188895096fd8d91d48753877729f4d37dd24
- https://github.com/buckyos/CYFS
- https://rustsec.org/advisories/RUSTSEC-2023-0046.html
