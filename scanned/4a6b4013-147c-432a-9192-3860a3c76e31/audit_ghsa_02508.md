# [H] Slock<T> allows sending non-Send types across thread boundaries

## Summary
Severity: High
Advisory: GHSA-83r8-p8v6-6gfm
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-83r8-p8v6-6gfm
Type: github-advisory

## Affected
- crates.io: `slock` — affected >=0 <0.2.0

## Details
`Slock<T>` unconditionally implements `Send`/`Sync`.

Affected versions of this crate allows sending non-Send types to other threads,
which can lead to data races and memory corruption due to the data race.

## References
- https://github.com/BrokenLamp/slock-rs/issues/2
- https://github.com/BrokenLamp/slock-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0135.html
