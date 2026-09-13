# [H] SyncChannel<T> can move 'T: !Send' to other threads

## Summary
Severity: High
Advisory: GHSA-8892-84wf-cg8f
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8892-84wf-cg8f
Type: github-advisory

## Affected
- crates.io: `signal-simple` — affected >=0

## Details
Affected versions of this crate unconditionally implement Send/Sync for `SyncChannel<T>`. `SyncChannel<T>` doesn't provide access to `&T` but merely serves as a channel that consumes and returns owned `T`. Users can create UB in safe Rust by sending `T: !Send` to other threads with `SyncChannel::send/recv` APIs. Using `T = Arc<Cell<_>` allows to create data races (which can lead to memory corruption), and using `T = MutexGuard<T>` allows to unlock a mutex from a thread that didn't lock the mutex.

## References
- https://github.com/kitsuneninetails/signal-rust/issues/2
- https://github.com/kitsuneninetails/signal-rust
- https://rustsec.org/advisories/RUSTSEC-2020-0126.html
