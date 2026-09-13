# [H] crayon: ObjectPool creates uninitialized memory when freeing objects

## Summary
Severity: High
Advisory: GHSA-xfhw-6mc4-mgxf
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-xfhw-6mc4-mgxf
Type: github-advisory

## Affected
- crates.io: `crayon` — affected >=0.6.0

## Details
As of version 0.6.0, the ObjectPool explicitly creates an uninitialized instance of its type parameter when it attempts to free an object, and swaps it into the storage. This causes instant undefined behavior due to reading the uninitialized memory in order to write it to the pool storage.

Extremely basic usage of the crate can trigger this issue, e.g. this code from a doctest:

```rust
use crayon::prelude::*;
application::oneshot().unwrap();

let mut params = MeshParams::default();

let mesh = video::create_mesh(params, None).unwrap();

// Deletes the mesh object.
video::delete_mesh(mesh); // <-- UB
```

The Clippy warning for this code was silenced in commit c2fde19caf6149d91faa504263f0bc5cafc35de5.

Discovered via https://asan.saethlin.dev/ub?crate=crayon&version=0.7.1

## References
- https://github.com/shawnscode/crayon/issues/109
- https://github.com/shawnscode/crayon/commit/c2fde19caf6149d91faa504263f0bc5cafc35de5
- https://github.com/shawnscode/crayon
- https://rustsec.org/advisories/RUSTSEC-2024-0018.html
