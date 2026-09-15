# [H] Improper privilege handling in Apache Accumulo

## Summary
Severity: High
Advisory: GHSA-grc3-8q8m-4j7c
CVE: CVE-2020-17533
CWE: CWE-252, CWE-280, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-grc3-8q8m-4j7c
Type: github-advisory

## Affected
- Maven: `org.apache.accumulo:accumulo-master` — affected >=1.5.0 <1.10.1
- Maven: `org.apache.accumulo:accumulo-master` — affected >=2.0.0 <2.0.1

## Details
Apache Accumulo versions 1.5.0 through 1.10.0 and version 2.0.0 do not properly check the return value of some policy enforcement functions before permitting an authenticated user to perform certain administrative operations. Specifically, the return values of the 'canFlush' and 'canPerformSystemActions' security functions are not checked in some instances, therefore allowing an authenticated user with insufficient permissions to perform the following actions: flushing a table, shutting down Accumulo or an individual tablet server, and setting or removing system-wide Accumulo configuration properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17533
- https://github.com/apache/accumulo/commit/56142a89952533fef922fa86739a879c073e7c2a
- https://github.com/apache/accumulo/commit/877ad502f6857e48342664e4b0ce83db74e4cda4
- https://github.com/apache/accumulo
- https://lists.apache.org/thread.html/rf8c1a787b6951d3dacb9ec58f0bf1633790c91f54ff10c6f8ff9d8ed%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rf8c1a787b6951d3dacb9ec58f0bf1633790c91f54ff10c6f8ff9d8ed%40%3Cuser.accumulo.apache.org%3E
- https://lists.apache.org/thread.html/rf8c1a787b6951d3dacb9ec58f0bf1633790c91f54ff10c6f8ff9d8ed@%3Cannounce.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/12/29/1
