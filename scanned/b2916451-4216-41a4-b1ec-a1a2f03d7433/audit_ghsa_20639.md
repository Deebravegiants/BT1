# [H] Apache Avro Rust SDK corrupted data read can cause crash

## Summary
Severity: High
Advisory: GHSA-3w5g-989p-35r8
CVE: CVE-2022-36125
CWE: CWE-190, CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-3w5g-989p-35r8
Type: github-advisory

## Affected
- crates.io: `apache-avro` — affected >=0 <0.14.0

## Details
It is possible to crash (panic) an application by providing a corrupted data to be read. This issue affects Rust applications using Apache Avro Rust SDK prior to 0.14.0 (previously known as avro-rs). Users should update to apache-avro version 0.14.0 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36125
- https://github.com/a0x8o/avro
- https://lists.apache.org/thread/t1r5xz0pvhm4tosqopjpj6dz8zlsht07
