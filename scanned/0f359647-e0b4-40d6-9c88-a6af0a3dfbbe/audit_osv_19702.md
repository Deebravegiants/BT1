# [M] CVE-2021-24117

## Summary
Severity: Medium
Advisory: CVE-2021-24117
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-14
Source: https://osv.dev/vulnerability/CVE-2021-24117
Type: osv

## Details
In Apache Teaclave Rust SGX SDK 1.1.3, a side-channel vulnerability in base64 PEM file decoding allows system-level (administrator) attackers to obtain information about secret RSA keys via a controlled-channel and side-channel attack on software running in isolated environments that can be single stepped, especially Intel SGX.

## References
- https://docs.rs/crate/sgx_tstd/1.1.1
- https://github.com/UzL-ITS/util-lookup/blob/main/cve-vulnerability-publication.md
- https://github.com/dingelish/rust-base64/commit/a554b7ae880553db6dde8a387101a093911d5b2a
