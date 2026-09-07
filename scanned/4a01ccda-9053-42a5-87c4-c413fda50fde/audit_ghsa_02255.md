# [M] Data race in eventio

## Summary
Severity: Medium
Advisory: GHSA-69vj-xx27-g45w
CVE: CVE-2020-36216
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-69vj-xx27-g45w
Type: github-advisory

## Affected
- crates.io: `eventio` — affected >=0 <0.5.1

## Details
Input<R> implements Send without requiring R: Send.

Affected versions of this crate allows users to send non-Send types to other threads, which can lead to undefined behavior such as data race and memory corruption.

The flaw was corrected in version 0.5.1 by adding R: Send bound to the Send impl of Input<R>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36216
- https://github.com/petabi/eventio/issues/33
- https://github.com/petabi/eventio
- https://rustsec.org/advisories/RUSTSEC-2020-0108.html
