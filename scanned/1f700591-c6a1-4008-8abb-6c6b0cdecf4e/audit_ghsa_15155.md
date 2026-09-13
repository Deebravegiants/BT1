# [M] Unsound sending of non-Send types across threads in threadalone

## Summary
Severity: Medium
Advisory: GHSA-w59h-378f-2frm
Ecosystem: crates.io
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-w59h-378f-2frm
Type: github-advisory

## Affected
- crates.io: `threadalone` — affected >=0 <0.2.1

## Details
Affected versions can run the `Drop` impl of a non-Send type on a different
thread than it was created on.

The flaw occurs when a stderr write performed by the `threadalone` crate fails,
for example because stderr is redirected to a location on a filesystem that is
full, or because stderr is a pipe that has been closed by the reader.

Dropping a non-Send type on the wrong thread is unsound. If used with a type
such as a pthread-based `MutexGuard`, [the consequence is undefined
behavior][mutexguard]. If used with `Rc`, there would be a data race on the
reference count, which is likewise undefined behavior.

[mutexguard]: https://github.com/rust-lang/rust/issues/23465#issuecomment-82730326

## References
- https://github.com/cr0sh/threadalone/issues/1
- https://rustsec.org/advisories/RUSTSEC-2024-0005.html
