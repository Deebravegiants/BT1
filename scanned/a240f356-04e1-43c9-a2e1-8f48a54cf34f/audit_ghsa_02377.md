# [M] Multiple soundness issues in cgc

## Summary
Severity: Medium
Advisory: GHSA-f3mq-99jr-ww4r
CVE: CVE-2020-36467
CWE: CWE-657
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-f3mq-99jr-ww4r
Type: github-advisory

## Affected
- crates.io: `cgc` — affected >=0

## Details
Affected versions of this crate have the following issues:

1. `Ptr` implements `Send` and `Sync` for all types, this can lead to data
   races by sending non-thread safe types across threads.

2. `Ptr::get` violates mutable alias rules by returning multiple mutable
   references to the same object.

3. `Ptr::write` uses non-atomic writes to the underlying pointer. This means
   that when used across threads it can lead to data races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36467
- https://github.com/playXE/cgc/issues/5
- https://github.com/playXE/cgc
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/cgc/RUSTSEC-2020-0148.md
- https://rustsec.org/advisories/RUSTSEC-2020-0148.html
