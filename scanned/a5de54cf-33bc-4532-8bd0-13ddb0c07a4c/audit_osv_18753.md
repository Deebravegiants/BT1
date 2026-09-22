# [C] CVE-2020-35863

## Summary
Severity: Critical
Advisory: CVE-2020-35863
Aliases: GHSA-h3qr-rq2j-74w4, RUSTSEC-2020-0008
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-31
Source: https://osv.dev/vulnerability/CVE-2020-35863
Type: osv

## Details
An issue was discovered in the hyper crate before 0.12.34 for Rust. HTTP request smuggling can occur. Remote code execution can occur in certain situations with an HTTP server on the loopback interface.

## References
- https://rustsec.org/advisories/RUSTSEC-2020-0008.html
