# [H] Data races in lever

## Summary
Severity: High
Advisory: GHSA-9pp4-8p8v-g78w
CVE: CVE-2020-36457
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9pp4-8p8v-g78w
Type: github-advisory

## Affected
- crates.io: `lever` — affected >=0 <0.1.1

## Details
An issue was discovered in the lever crate before 0.1.1 for Rust. AtomicBox<T> implements the Send and Sync traits for all types T. This allows non-Send types such as Rc and non-Sync types such as Cell to be used across thread boundaries which can trigger undefined behavior and memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36457
- https://github.com/vertexclique/lever/issues/15
- https://github.com/vertexclique/lever/pull/17
- https://github.com/vertexclique/lever/commit/4a4cca61cdb25061967d58522229e147483007b1
- https://github.com/vertexclique/lever
- https://rustsec.org/advisories/RUSTSEC-2020-0137.html
