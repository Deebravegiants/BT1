# [H] Data races in multiqueue

## Summary
Severity: High
Advisory: GHSA-r2x6-vrxx-jgv4
CVE: CVE-2020-36463
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r2x6-vrxx-jgv4
Type: github-advisory

## Affected
- crates.io: `multiqueue` — affected >=0

## Details
Affected versions of this crate unconditionally implemented Send for types used in queue implementations (InnerSend<RW, T>, InnerRecv<RW, T>, FutInnerSend<RW, T>, FutInnerRecv<RW, T>). This allows users to send non-Send types to other threads, which can lead to data race bugs or other undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36463
- https://github.com/schets/multiqueue/issues/31
- https://github.com/schets/multiqueue
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/multiqueue/RUSTSEC-2020-0143.md
- https://rustsec.org/advisories/RUSTSEC-2020-0143.html
