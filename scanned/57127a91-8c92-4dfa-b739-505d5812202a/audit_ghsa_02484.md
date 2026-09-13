# [C] Use after free in portaudio-rs

## Summary
Severity: Critical
Advisory: GHSA-qpjr-ch72-2qq4
CVE: CVE-2019-16881
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qpjr-ch72-2qq4
Type: github-advisory

## Affected
- crates.io: `portaudio-rs` — affected >=0 <0.3.2

## Details
Affected versions of this crate is not panic safe within callback functions stream_callback and stream_finished_callback. The call to user-provided closure might panic before a mem::forget call, which then causes a use after free that grants attacker to control the callback function pointer. This allows an attacker to construct an arbitrary code execution .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16881
- https://github.com/mvdnes/portaudio-rs/issues/20
- https://github.com/mvdnes/portaudio-rs/commit/7466df019f6739732fd91401017942c22364ef61
- https://github.com/mvdnes/portaudio-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0022.html
