# [M] libdav1d-sys affected by dav1d AV1 decoder integer overflow

## Summary
Severity: Medium
Advisory: GHSA-mc39-h54g-pvw6
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-mc39-h54g-pvw6
Type: github-advisory

## Affected
- crates.io: `libdav1d-sys` — affected >=0 <0.7.0

## Details
An integer overflow in dav1d AV1 decoder that can occur when decoding videos with large frame size. This can lead to memory corruption within the AV1 decoder. We recommend upgrading to version 0.7.0 of libdav1d-sys, which includes dav1d 1.4.0.

## References
- https://github.com/njaard/libavif-rs
- https://rustsec.org/advisories/RUSTSEC-2024-0016.html
- https://www.cvedetails.com/cve/CVE-2024-1580
