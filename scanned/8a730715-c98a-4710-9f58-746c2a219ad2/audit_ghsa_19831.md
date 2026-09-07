# [M] Crash due to uncontrolled recursion in protobuf crate

## Summary
Severity: Medium
Advisory: GHSA-2gh3-rmm4-6rq5
CVE: CVE-2025-53605
CWE: CWE-20, CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-2gh3-rmm4-6rq5
Type: github-advisory

## Affected
- crates.io: `protobuf` — affected >=0 <3.7.2

## Details
Affected version of this crate did not properly parse unknown fields when parsing a user-supplied input.

This allows an attacker to cause a stack overflow when parsing the message on untrusted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53605
- https://github.com/stepancheg/rust-protobuf/issues/749
- https://github.com/stepancheg/rust-protobuf/commit/f06992f46771c0a092593b9ebf7afd48740b3ed6
- https://github.com/stepancheg/rust-protobuf
- https://rustsec.org/advisories/RUSTSEC-2024-0437.html
