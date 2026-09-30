# [H] OpenH264 Rust API Openh264 Decoding Functions Heap Overflow Vulnerability

## Summary
Severity: High
Advisory: GHSA-5pmw-9j92-3c4c
CWE: CWE-122, CWE-1395
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-5pmw-9j92-3c4c
Type: github-advisory

## Affected
- crates.io: `openh264-sys2` — affected >=0 <0.8.0

## Details
OpenH264 recently reported a [heap overflow](https://github.com/cisco/openh264/security/advisories/GHSA-m99q-5j7x-7m9x) that was fixed in upstream [63db555](https://github.com/cisco/openh264/commit/63db555e30986e3a5f07871368dc90ae78c27449) and [integrated into](https://github.com/ralfbiedert/openh264-rs/commit/3a822fff0b4c9a984622ca2b179fe8898ac54b14) our 0.6.6 release. For users relying on Cisco's pre-compiled DLL, we also published 0.8.0, which is compatible with their latest fixed DLL version  2.6.0. 

In other words:
- if you rely on our `source` feature only, >=0.6.6 should be safe,
- if you rely on `libloading`, you must upgrade to 0.8.0 _and_ use their latest DLL >=2.6.0. 

Users handling untrusted video files should update immediately.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27091
- https://github.com/cisco/openh264/pull/3818
- https://github.com/ralfbiedert/openh264-rs/commit/3a822fff0b4c9a984622ca2b179fe8898ac54b14
- https://github.com/ralfbiedert/openh264-rs
- https://rustsec.org/advisories/RUSTSEC-2025-0008.html
