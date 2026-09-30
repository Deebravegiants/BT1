# [H] JDBC URL bypassing by allowLoadLocalInfileInPath param

## Summary
Severity: High
Advisory: GHSA-pq67-9jf9-hc3c
CVE: CVE-2023-34434
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-pq67-9jf9-hc3c
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.8.0

## Details
Deserialization of Untrusted Data Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.7.0. 

The attacker could bypass the current logic and achieve arbitrary file reading. To solve it, users are advised to upgrade to Apache InLong's 1.8.0 or cherry-pick  https://github.com/apache/inlong/pull/8130 .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34434
- https://github.com/apache/inlong/pull/8130
- https://github.com/apache/inlong/commit/34835f827771074345f42a9b1658d018f202516e
- https://github.com/apache/inlong
- https://lists.apache.org/thread/7f1o71w5r732cspltmtdydn01gllf4jo
- http://seclists.org/fulldisclosure/2023/Jul/43
- http://www.openwall.com/lists/oss-security/2023/07/25/3
