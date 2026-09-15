# [H] Apache SeaTunnel SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-8m84-h9hh-3cfh
CVE: CVE-2023-49198
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-8m84-h9hh-3cfh
Type: github-advisory

## Affected
- Maven: `org.apache.seatunnel:seatunnel` — affected >=1.0.0 <1.0.1

## Details
Mysql security vulnerability in Apache SeaTunnel.

Attackers can read files on the MySQL server by modifying the information in the MySQL URL

 allowLoadLocalInfile=true&allowUrlInLocalInfile=true&allowLoadLocalInfileInPath=/&maxAllowedPacket=655360
This issue affects Apache SeaTunnel: 1.0.0.

Users are recommended to upgrade to version [1.0.1], which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49198
- https://github.com/apache/seatunnel
- https://lists.apache.org/thread/48j9f1nsn037mgzc4j9o51nwglb1s08h
