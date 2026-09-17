# [H] Apache Avro Rust SDK vulnerable to reader looping in cycle endlessly, consuming CPU

## Summary
Severity: High
Advisory: GHSA-v456-chpw-6mmw
CVE: CVE-2022-35724
CWE: CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-v456-chpw-6mmw
Type: github-advisory

## Affected
- crates.io: `apache-avro` — affected >=0 <0.14.0

## Details
It is possible to provide data to be read that leads the reader to loop in cycles endlessly, consuming CPU. This issue affects Rust applications using Apache Avro Rust SDK prior to 0.14.0 (previously known as avro-rs). Users should update to apache-avro version 0.14.0 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35724
- https://github.com/a0x8o/avro
- https://lists.apache.org/thread/771z1nwrpkn1ovmyfb2fm65mchdxgy7p
