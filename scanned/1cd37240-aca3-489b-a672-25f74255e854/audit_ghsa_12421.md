# [M] unsafe-libyaml unaligned write of u64 on 32-bit and 16-bit platforms

## Summary
Severity: Medium
Advisory: GHSA-r24f-hg58-vfrw
Ecosystem: crates.io
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-r24f-hg58-vfrw
Type: github-advisory

## Affected
- crates.io: `unsafe-libyaml` — affected >=0 <0.2.10

## Details
Affected versions allocate memory using the alignment of `usize` and write data to it of type `u64`, without using `core::ptr::write_unaligned`. In platforms with sub-64bit alignment for `usize` (including wasm32 and x86) these writes are insufficiently aligned some of the time.

If using an ordinary optimized standard library, the bug exhibits Undefined Behavior so may or may not behave in any sensible way, depending on optimization settings and hardware and other things. If using a Rust standard library built with debug assertions enabled, the bug manifests deterministically in a crash (non-unwinding panic) saying _"ptr::write requires that the pointer argument is aligned and non-null"_.

No 64-bit platform is impacted by the bug.

The flaw was corrected by allocating with adequately high alignment on all
platforms.

## References
- https://github.com/dtolnay/unsafe-libyaml/issues/21
- https://github.com/dtolnay/unsafe-libyaml/commit/7755559145c9cf5573639bfecc557893d4a46b0d
- https://github.com/dtolnay/unsafe-libyaml
- https://rustsec.org/advisories/RUSTSEC-2023-0075.html
