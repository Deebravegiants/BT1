# [C] Double free in crossbeam

## Summary
Severity: Critical
Advisory: GHSA-c3cw-c387-pj65
CVE: CVE-2018-20996
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c3cw-c387-pj65
Type: github-advisory

## Affected
- crates.io: `crossbeam` — affected >=0.4.0 <0.4.1

## Details
Even if an element is popped from a queue, crossbeam would run its destructor inside the epoch-based garbage collector. This is a source of double frees.

The flaw was corrected by wrapping elements inside queues in a ManuallyDrop.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20996
- https://github.com/crossbeam-rs/crossbeam-epoch/issues/82
- https://github.com/crossbeam-rs/crossbeam-epoch
- https://rustsec.org/advisories/RUSTSEC-2018-0009.html
