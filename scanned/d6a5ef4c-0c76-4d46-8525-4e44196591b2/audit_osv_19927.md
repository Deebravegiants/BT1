# [H] CVE-2021-28036

## Summary
Severity: High
Advisory: CVE-2021-28036
Aliases: GHSA-fhv4-fx3v-77w6, RUSTSEC-2021-0035
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-28036
Type: osv

## Details
An issue was discovered in the quinn crate before 0.7.0 for Rust. It may have invalid memory access for certain versions of the standard library because it relies on a direct cast of std::net::SocketAddrV4 and std::net::SocketAddrV6 data structures.

## References
- https://rustsec.org/advisories/RUSTSEC-2021-0035.html
