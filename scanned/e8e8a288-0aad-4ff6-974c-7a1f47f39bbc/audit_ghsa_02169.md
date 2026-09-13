# [H] Data races in signal-simple

## Summary
Severity: High
Advisory: GHSA-36cg-4jff-5863
CVE: CVE-2020-36446
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-36cg-4jff-5863
Type: github-advisory

## Affected
- crates.io: `signal-simple` — affected >=0

## Details
Affected versions of this crate unconditionally implement Send/Sync for SyncChannel<T>. SyncChannel<T> doesn't provide access to &T but merely serves as a channel that consumes and returns owned T.

Users can create UB in safe Rust by sending T: !Send to other threads with SyncChannel::send/recv APIs. Using T = Arc<Cell<_> allows to create data races (which can lead to memory corruption), and using T = MutexGuard<T> allows to unlock a mutex from a thread that didn't lock the mutex.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36446
- https://github.com/kitsuneninetails/signal-rust/issues/2
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/signal-simple/RUSTSEC-2020-0126.md
- https://rustsec.org/advisories/RUSTSEC-2020-0126.html
- http://github.com/kitsuneninetails/signal-rust
