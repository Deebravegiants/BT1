# [C] Integer overflow in base64

## Summary
Severity: Critical
Advisory: GHSA-x67x-vg9m-65c3
CVE: CVE-2017-1000430
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-x67x-vg9m-65c3
Type: github-advisory

## Affected
- crates.io: `base64` — affected >=0 <0.5.2

## Details
Affected versions of this crate suffered from an integer overflow bug when
calculating the size of a buffer to use when encoding base64 using the
`encode_config_buf` and `encode_config` functions.  If the input string
was large, this would cause a buffer to be allocated that was too small.
Since this function writes to the buffer using unsafe code, it would
allow an attacker to write beyond the buffer, causing memory corruption
and possibly the execution of arbitrary code.

This flaw was corrected by using checked arithmetic to calculate
the size of the buffer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000430
- https://github.com/alicemaz/rust-base64/commit/24ead980daf11ba563e4fb2516187a56a71ad319
- https://github.com/alicemaz/rust-base64
- https://rustsec.org/advisories/RUSTSEC-2017-0004.html
