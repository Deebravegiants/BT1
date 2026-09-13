# [C] nb-connect invalidly assumes the memory layout of std::net::SocketAddr

## Summary
Severity: Critical
Advisory: GHSA-rm4w-6696-r77p
CVE: CVE-2021-27376
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rm4w-6696-r77p
Type: github-advisory

## Affected
- crates.io: `nb-connect` — affected >=0 <1.0.3

## Details
The nb-connect crate has assumed std::net::SocketAddrV4 and std::net::SocketAddrV6 have the same memory layout as the system C representation sockaddr. It has simply casted the pointers to convert the socket addresses to the system representation. The standard library does not say anything about the memory layout, and this will cause invalid memory access if the standard library changes the implementation. No warnings or errors will be emitted once the change happens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27376
- https://github.com/smol-rs/nb-connect/issues/1
- https://github.com/smol-rs/nb-connect
- https://rustsec.org/advisories/RUSTSEC-2021-0021.html
