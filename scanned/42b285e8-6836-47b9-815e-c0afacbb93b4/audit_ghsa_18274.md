# [M] ArrayQueue's push_front is not panic-safe

## Summary
Severity: Medium
Advisory: GHSA-xqjr-wfx3-gmxv
CWE: CWE-665
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-xqjr-wfx3-gmxv
Type: github-advisory

## Affected
- crates.io: `array-queue` — affected >=0.3.0 <0.4.0

## Details
The safe API `array_queue::ArrayQueue::push_front` can lead to deallocating uninitialized memory if a panic occurs while invoking the `clone` method on the passed argument.

Specifically, `push_front` receives an argument that is intended to be cloned and pushed, whose type implements the `Clone` trait. Furthermore, the method updates the queue's `start` index before initializing the slot for the newly pushed element. User-defined implementations of `Clone` may include a `clone` method that can panic. If such a panic occurs during initialization, the structure is left with an advanced `start` index pointing to an uninitialized slot. When `ArrayQueue` is later dropped, its destructor treats that slot as initialized and attempts to drop it, resulting in an attempt to free uninitialized memory.

The bug was fixed in commit `728fe1b`.

## References
- https://github.com/raviqqe/array-queue/issues/3
- https://github.com/raviqqe/array-queue/commit/728fe1bdffb04896d218e962d989a2ae6bf1ea92
- https://github.com/raviqqe/array-queue
- https://rustsec.org/advisories/RUSTSEC-2025-0054.html
