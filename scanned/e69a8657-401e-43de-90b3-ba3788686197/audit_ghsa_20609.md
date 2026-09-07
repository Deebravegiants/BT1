# [H] Apache Avro Rust SDK's Reader could consume memory beyond allowed constraints

## Summary
Severity: High
Advisory: GHSA-wcm8-86x6-8mv3
CVE: CVE-2022-36124
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-wcm8-86x6-8mv3
Type: github-advisory

## Affected
- crates.io: `apache-avro` — affected >=0 <0.14.0

## Details
It is possible for a Reader to consume memory beyond the allowed constraints and thus lead to out of memory on the system. This issue affects Rust applications using Apache Avro Rust SDK prior to 0.14.0 (previously known as avro-rs). Users should update to apache-avro version 0.14.0 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36124
- https://github.com/a0x8o/avro
- https://github.com/pypa/advisory-database/tree/main/vulns/avro/PYSEC-2022-43180.yaml
- https://lists.apache.org/thread/kj429rzo1xxjgz058qqqg0y7c0p512zo
