# [M] AtomicBucket<T> unconditionally implements Send/Sync

## Summary
Severity: Medium
Advisory: GHSA-3hxh-7jxm-59x4
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-3hxh-7jxm-59x4
Type: github-advisory

## Affected
- crates.io: `metrics-util` — affected >=0 <0.7.0

## Details
In the affected versions of the crate, `AtomicBucket<T>` unconditionally implements `Send`/`Sync` traits. Therefore, users can create a data race to the inner
`T: !Sync` by using the `AtomicBucket::data_with()` API.
Such data races can potentially cause memory corruption or other undefined behavior.

The flaw was fixed in commit 8e6daab by adding appropriate Send/Sync bounds to the Send/Sync impl of struct `Block<T>` (which is a data type contained inside `AtomicBucket<T>`).

## References
- https://github.com/metrics-rs/metrics/issues/190
- https://github.com/metrics-rs/metrics
- https://rustsec.org/advisories/RUSTSEC-2021-0113.html
