# [H] Uncontrolled memory consumption in protobuf

## Summary
Severity: High
Advisory: GHSA-mh6h-f25p-98f8
CVE: CVE-2019-15544
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mh6h-f25p-98f8
Type: github-advisory

## Affected
- crates.io: `protobuf` — affected >=0 <2.6.0

## Details
Affected versions of this crate called Vec::reserve() on user-supplied input. This allows an attacker to cause an Out of Memory condition while calling the vulnerable method on untrusted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15544
- https://github.com/stepancheg/rust-protobuf/issues/411
- https://github.com/stepancheg/rust-protobuf
- https://lists.apache.org/thread.html/r00097d0b5b6164ea428554007121d5dc1f88ba2af7b9e977a10572cd@%3Cdev.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r4ef574a5621b0e670a3ce641e9922543e34f22bf4c9ee9584aa67fcf@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r7fed8dd9bee494094e7011cf3c2ab75bd8754ea314c6734688c42932@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/rd64381fb8f92d640c1975dc50dcdf1b8512e02a2a7b20292d3565cae@%3Cissues.hbase.apache.org%3E
- https://rustsec.org/advisories/RUSTSEC-2019-0003.html
