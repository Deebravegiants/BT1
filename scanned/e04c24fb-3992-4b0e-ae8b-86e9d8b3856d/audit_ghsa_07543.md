# [H] jxl-grid on 32-bit platforms has an out-of-bounds writes due to integer overflow

## Summary
Severity: High
Advisory: GHSA-5pmv-rx8r-wmv5
CVE: CVE-2026-52834
CWE: CWE-122, CWE-131, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-5pmv-rx8r-wmv5
Type: github-advisory

## Affected
- crates.io: `jxl-grid` — affected >=0 <0.6.2

## Details
### Summary

On 32-bit platforms, decoding a crafted image may lead to out-of-bounds writes due to integer overflow in length calculation.

### Details & PoC

The test listed below fail under miri with command `cargo +nightly miri test --release -p jxl-grid`

Or you can use Address Sanitizer, which ignores Rust-specific UB like aliasing but still flags out-of-bounds accesses:

`RUSTFLAGS=-Zsanitizer=address cargo +nightly test -Zbuild-std -p jxl-grid --release --target x86_64-unknown-linux-gnu`

The following tests should be appended to `crates/jxl-grid/src/test/subgrids.rs`:

```rust
mod miri_ub {
    use super::*;

    // `AlignedGrid::with_alloc_tracker` computes `width * height` unchecked. In release, overflow
    // can create a tiny backing buffer for huge logical dimensions.
    #[test]
    fn aligned_grid_dimension_product_overflows() {
        let width = usize::MAX / 2 + 1;
        let mut grid = AlignedGrid::<u8>::with_alloc_tracker(width, 2, None).unwrap();
        let mut subgrid = grid.as_subgrid_mut();
        *subgrid.get_mut(0, 1) = 1;
        std::hint::black_box(grid);
    }
}
```

This issue can be reachable through decoding a crafted image in two ways:

1. **Huge actual frame**
   A frame such as `65536 x 65536` passes the current frame area limit (`2^32 <= 2^40`) but overflows `usize` element count on 32-bit. Rendering then allocates too-small `AlignedGrid`s in modular/VarDCT/filter paths and later writes through mutable subgrids.

2. **Huge canvas plus tiny cropped frame**
   This is the more practical “small payload, huge logical output” case. A bitstream-controlled frame crop can be tiny, but if the canvas/default requested region is huge, composition can allocate an output grid sized to the canvas/ROI at crates/jxl-render/src/blend.rs. That is bitstream frame cropping, not API crop. With a 32-bit target and a full requested image region whose area overflows, this can happen through ordinary `render_frame()`.

### Impact

On 32-bit platforms this can cause out-of-bounds writes with attacker-controlled data when decoding a crafted JPEG XL image. This could allow arbitrary code execution.

## References
- https://github.com/tirr-c/jxl-oxide/security/advisories/GHSA-5pmv-rx8r-wmv5
- https://github.com/tirr-c/jxl-oxide
- https://rustsec.org/advisories/RUSTSEC-2026-0151.html
