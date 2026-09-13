# [H] Out of bounds read in simd-json

## Summary
Severity: High
Advisory: GHSA-gwfj-pw2x-h6c2
CVE: CVE-2019-15550
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gwfj-pw2x-h6c2
Type: github-advisory

## Affected
- crates.io: `simd-json` — affected >=0.1.13 <0.1.15

## Details
The affected version of this crate did not guard against accessing memory beyond the range of its input data. A pointer cast to read the data into a 256-bit register could lead to a segmentation fault when the end plus the 32 bytes (256 bit) read would overlap into the next page during string parsing. This allows an attacker to eventually crash a service. The flaw was corrected by using a padding buffer for the last read from the input. So that we are we never read over the boundary of the input data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15550
- https://github.com/Licenser/simdjson-rs/pull/27
- https://github.com/Licenser/simdjson-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0008.html
