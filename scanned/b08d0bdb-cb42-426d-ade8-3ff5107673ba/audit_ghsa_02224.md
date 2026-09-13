# [M] Segmentation fault in time

## Summary
Severity: Medium
Advisory: GHSA-wcg3-cvx6-7396
CVE: CVE-2020-26235
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wcg3-cvx6-7396
Type: github-advisory

## Affected
- crates.io: `time` — affected >=0.1.0 <0.2.23
- crates.io: `time` — affected >=0.2.7 <0.2.23

## Details
### Impact

Unix-like operating systems may segfault due to dereferencing a dangling pointer in specific circumstances. This requires an environment variable to be set in a different thread than the affected functions. This may occur without the user's knowledge, notably in a third-party library.

The affected functions from time 0.2.7 through 0.2.22 are:

- `time::UtcOffset::local_offset_at`
- `time::UtcOffset::try_local_offset_at`
- `time::UtcOffset::current_local_offset`
- `time::UtcOffset::try_current_local_offset`
- `time::OffsetDateTime::now_local`
- `time::OffsetDateTime::try_now_local`

The affected functions in time 0.1 (all versions) are:

- `at`
- `at_utc`
- `now`

Non-Unix targets (including Windows and wasm) are unaffected.

### Patches

In some versions of `time`, the internal method that determines the local offset has been modified to always return `None` on the affected operating systems. This has the effect of returning an `Err` on the `try_*` methods and `UTC` on the non-`try_*` methods. In later versions, `time` will attempt to determine the number of threads running in the process. If the process is single-threaded, the call will proceed as its safety invariant is upheld.

Users and library authors with time in their dependency tree must perform `cargo update`, which will pull in the updated, unaffected code.

Users of time 0.1 do not have a patch and must upgrade to an unaffected version: time 0.2.23 or greater or the 0.3 series.

### Workarounds

Library authors must ensure that the program only has one running thread at the time of calling any affected method. Binary authors may do the same and/or ensure that no other thread is actively mutating the environment.

### References

[time-rs/time#293](https://github.com/time-rs/time/issues/293).

## References
- https://github.com/time-rs/time/security/advisories/GHSA-wcg3-cvx6-7396
- https://nvd.nist.gov/vuln/detail/CVE-2020-26235
- https://github.com/time-rs/time/issues/293
- https://crates.io/crates/time/0.2.23
- https://github.com/time-rs/time
- https://rustsec.org/advisories/RUSTSEC-2020-0071.html
