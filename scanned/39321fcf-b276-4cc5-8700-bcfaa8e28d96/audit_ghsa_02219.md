# [M] Data races in multiqueue2

## Summary
Severity: Medium
Advisory: GHSA-jphw-p3m6-pj3c
CVE: CVE-2020-36214
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jphw-p3m6-pj3c
Type: github-advisory

## Affected
- crates.io: `multiqueue2` — affected >=0 <0.1.7

## Details
Affected versions of this crate unconditionally implemented Send for types used in queue implementations (InnerSend<RW, T>, InnerRecv<RW, T>, FutInnerSend<RW, T>, FutInnerRecv<RW, T>).

This allows users to send non-Send types to other threads, which can lead to data race bugs or other undefined behavior.

The flaw was corrected in v0.1.7 by adding T: Send bound to to the Send impl of four data types explained above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36214
- https://github.com/abbychau/multiqueue2/issues/10
- https://github.com/abbychau/multiqueue2
- https://rustsec.org/advisories/RUSTSEC-2020-0106.html
