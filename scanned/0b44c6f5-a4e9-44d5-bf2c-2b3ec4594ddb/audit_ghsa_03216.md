# [M] Uncontrolled Resource Consumption in Apache Tika

## Summary
Severity: Medium
Advisory: GHSA-3h29-52vh-pqgr
CVE: CVE-2020-1950
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-3h29-52vh-pqgr
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika` — affected >=1.0 <1.24

## Details
A carefully crafted or corrupt PSD file can cause excessive memory usage in Apache Tika's PSDParser in versions 1.0-1.23.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1950
- https://github.com/apache/tika
- https://lists.apache.org/thread.html/r463b1a67817ae55fe022536edd6db34e8f9636971188430cbcf8a8dd%40%3Cdev.tika.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/03/msg00035.html
- https://usn.ubuntu.com/4564-1
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
