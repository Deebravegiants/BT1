# [H] Improper Input Validation in Parquet-MR

## Summary
Severity: High
Advisory: GHSA-gc67-crq6-hgh5
CVE: CVE-2021-41561
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-gc67-crq6-hgh5
Type: github-advisory

## Affected
- Maven: `org.apache.parquet:parquet` — affected >=1.12.0 <1.12.2
- Maven: `org.apache.parquet:parquet` — affected >=0 <1.11.2

## Details
Improper Input Validation vulnerability in Parquet-MR of Apache Parquet allows an attacker to DoS by malicious Parquet files. This issue affects Apache Parquet-MR version 1.9.0 and later versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41561
- https://github.com/apache/parquet-mr
- https://lists.apache.org/thread/1bjlscbqtfzl160hrm9lnpjpppp5z3zr
- http://www.openwall.com/lists/oss-security/2021/12/20/1
