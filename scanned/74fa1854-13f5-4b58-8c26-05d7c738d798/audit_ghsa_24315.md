# [H] futures_task::waker may cause a use-after-free if used on a type that isn't 'static

## Summary
Severity: High
Advisory: GHSA-r93v-9p5q-vhpf
CVE: CVE-2020-35906
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r93v-9p5q-vhpf
Type: github-advisory

## Affected
- crates.io: `futures-task` — affected >=0.2.1 <0.3.6

## Details
Affected versions of the crate did not properly implement a 'static lifetime bound on the waker function. This resulted in a use-after-free if Waker::wake() is called after original data had been dropped.

The flaw was corrected by adding 'static lifetime bound to the data waker takes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35906
- https://github.com/rust-lang/futures-rs/pull/2206
- https://github.com/rust-lang/futures-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0060.html
