# [H] Data races in multiqueue

## Summary
Severity: High
Advisory: GHSA-jf43-3v8j-qwwr
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jf43-3v8j-qwwr
Type: github-advisory

## Affected
- crates.io: `multiqueue` — affected >=0

## Details
Affected versions of multiqueue unconditionally implemented `Send` for types used in queue implementations (`InnerSend<RW, T>`, `InnerRecv<RW, T>`, `FutInnerSend<RW, T>`, `FutInnerRecv<RW, T>`). This allows users to send non-Send types to other threads, which can lead to data race bugs or other undefined behavior.

## References
- https://github.com/schets/multiqueue/issues/31
- https://github.com/schets/multiqueue
- https://rustsec.org/advisories/RUSTSEC-2020-0143.html
