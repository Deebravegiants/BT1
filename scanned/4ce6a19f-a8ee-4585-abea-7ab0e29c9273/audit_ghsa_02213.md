# [M] Source code is downloaded over cleartext HTTP in portaudio

## Summary
Severity: Medium
Advisory: GHSA-pq6v-x7gp-7776
CVE: CVE-2016-10933
CWE: CWE-319
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-pq6v-x7gp-7776
Type: github-advisory

## Affected
- crates.io: `portaudio` — affected >=0

## Details
An issue was discovered in the portaudio crate through 0.7.0 for Rust. There is a man-in-the-middle issue because the source code is downloaded over cleartext HTTP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10933
- https://github.com/RustAudio/rust-portaudio/issues/144
- https://github.com/RustAudio/rust-portaudio
- https://rustsec.org/advisories/RUSTSEC-2016-0003.html
