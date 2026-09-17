# [H] wasmtime-wasi: WASI path_open(TRUNCATE) bypasses `FilePerms::WRITE` host restriction

## Summary
Severity: High
Advisory: GHSA-2r75-cxrj-cmph
CVE: CVE-2026-47261
CWE: CWE-284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-2r75-cxrj-cmph
Type: github-advisory

## Affected
- crates.io: `wasmtime-wasi` — affected >=37.0.0 <44.0.2
- crates.io: `wasmtime-wasi` — affected >=25.0.0 <36.0.10
- crates.io: `wasmtime-wasi` — affected >=0 <24.0.9

## Details
## Summary

In `wasmtime-wasi`, when a filesystem preopen is given `DirPerms::all()` and `FilePerms::READ` without `FilePerms::WRITE`,  this wasmtime-wasi enforced access control mechanism can be bypassed by using the wasip2 `descriptor.open-at` or wasip1 `path_open` interfaces by opening a file with `OpenFlags::TRUNCATE` oflag only, for example:

```rust
dir_descriptor.open_at(
   PathFlags::empty(),
   FILENAME,
   OpenFlags::TRUNCATE,
   DescriptorFlags::READ,
)
```

```rust
wasip1::path_open(
    dir_fd,
    0,
    FILENAME,
    wasip1::OFLAGS_TRUNC,
    wasip1::RIGHTS_FD_READ,
    0,
    0
)
```

The root cause is that the clause that considered `OpenFlags::TRUNCATE` did not set `open_mode |= OpenMode::WRITE;`, used later in that function for the access control check against `FilePerms` for whether opening that file is permitted. With the bug corrected, these calls to `open-at` and `path_open` fail with `error-code.not-permitted` and `ERRNO_PERM` respectively.

The bug in `crates/wasi/src/filesystem.rs`, `Dir::open_at`, lines 967–969:

```rust
if oflags.contains(OpenFlags::TRUNCATE) {
    opts.truncate(true).write(true);
}
```
and the single line fix is:
```rust
if oflags.contains(OpenFlags::TRUNCATE) {
    opts.truncate(true).write(true);
    open_mode |= OpenMode::WRITE;
}
```

Only wasmtime-wasi embeddings that use a combination of DirPerms::MUTATE with FilePerms::READ are affected by this bug, e.g. those that use in the `WasiCtxBuilder`:
```rust
builder.preopened_dir("readonly", "readonly", DirPerms::READ | DirPerms::MUTATE, FilePerms::READ);
```

In particular, the Wasmtime project's `wasmtime-cli`'s use of wasmtime-wasi is not affected, because it always sets `FilePerms::all()` for all preopens.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-2r75-cxrj-cmph
- https://nvd.nist.gov/vuln/detail/CVE-2026-47261
- https://github.com/bytecodealliance/wasmtime
- https://github.com/bytecodealliance/wasmtime/releases/tag/v24.0.9
- https://github.com/bytecodealliance/wasmtime/releases/tag/v36.0.10
- https://github.com/bytecodealliance/wasmtime/releases/tag/v44.0.2
- https://github.com/bytecodealliance/wasmtime/releases/tag/v45.0.0
- https://rustsec.org/advisories/RUSTSEC-2026-0149.html
