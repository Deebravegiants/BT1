# [C] Deserializing an array can free uninitialized memory in byte_struct

## Summary
Severity: Critical
Advisory: GHSA-8fgg-5v78-6g76
CVE: CVE-2021-28033
CWE: CWE-119, CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8fgg-5v78-6g76
Type: github-advisory

## Affected
- crates.io: `byte_struct` — affected >=0 <0.6.1

## Details
Byte_struct stack and unpack structure as raw bytes with packed or bit field layout. An issue was discovered in the byte_struct crate before 0.6.1 for Rust. There can be a drop of uninitialized memory if a certain deserialization method panics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28033
- https://github.com/wwylele/byte-struct-rs/issues/1
- https://github.com/wwylele/byte-struct-rs/commit/a535678377de12bc6bc22620c5f59bcc1369f76f
- https://github.com/wwylele/byte-struct-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0032.html
