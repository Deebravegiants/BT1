# [M] Grid: Integer Overflow in Grid::expand_rows Leads to Safe-API Undefined Behavior

## Summary
Severity: Medium
Advisory: GHSA-38c5-483c-4qqp
CVE: CVE-2026-42199
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-38c5-483c-4qqp
Type: github-advisory

## Affected
- crates.io: `grid` — affected >=0.17.0 <1.0.1

## Details
### Summary
An integer overflow in `Grid::expand_rows()` can corrupt the relationship between the grid’s logical dimensions and its backing storage. After the internal invariant is broken, the safe API get() may invoke get_unchecked() with an invalid index, resulting in Undefined Behavior.

### Details
Tested Version: grid = "1.0.0"

expand_rows() computes the new backing length using unchecked arithmetic:

`self.data.len() + rows * self.cols
`

If rows * self.cols or the subsequent addition overflows usize, the result wraps in release builds and self.data may be resized to a length much smaller than logically required.

After that, if the grid is in ColumnMajor order, the function performs in-place rotation using indices derived from:

```
let total_rows = self.rows + row_added;
let col_idx = i * total_rows;
self.data[col_idx..col_idx + total_rows + i].rotate_right(i);
```

These computations also rely on the assumption that the backing storage has been resized to the correct length. Once the earlier length computation has wrapped, this assumption no longer holds, so the function may operate on invalid ranges or otherwise enter an inconsistent state.

Finally, the function updates logical metadata with:

`self.rows += rows;
`

As a result, the grid can end up with logical dimensions that no longer match the actual backing storage. Subsequent safe API calls such as get() may then rely on corrupted metadata and reach unsafe internal accesses, resulting in invalid unchecked access and Undefined Behavior.

### PoC
```rust
#![forbid(unsafe_code)]

use grid::Grid;

fn main() {
    let mut g = Grid::from_vec(vec![1u8, 2u8], 2);

    g.expand_rows(usize::MAX / 2);

    g.get(0, 0); // triggers UB in get_unchecked
}
```

### Impact
- Invalid unchecked access (`get_unchecked`) reached via safe API
- Confirmed by Miri (release-mode):

```
error: Undefined Behavior: `assume` called with `false`
   --> ..../grid-1.0.0/src/lib.rs:527:9
    |
527 |         self.data.get_unchecked(index)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here

```
- Potential crash / denial of service in release-builds (e.g., SIGSEGV, Illegal instruction)
- Violates Rust’s safety guarantees despite using only safe code

## References
- https://github.com/becheran/grid/security/advisories/GHSA-38c5-483c-4qqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42199
- https://github.com/becheran/grid/commit/be213bd3528727148bef2d523c89e95d1fd9c072
- https://github.com/becheran/grid
- https://github.com/becheran/grid/releases/tag/v1.0.1
