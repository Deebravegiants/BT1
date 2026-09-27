# [H] Apache InLong Exposure of Resource to Wrong Sphere vulnerability

## Summary
Severity: High
Advisory: GHSA-7mhc-76hf-3jp9
CVE: CVE-2023-31103
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-7mhc-76hf-3jp9
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-dao` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-service` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-test` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-web` — affected >=1.4.0 <1.7.0

## Details
Exposure of Resource to Wrong Sphere Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.6.0.  Attackers can change the immutable name and type of cluster of InLong. Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7891 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31103
- https://github.com/apache/inlong/pull/7891
- https://github.com/apache/inlong
- https://lists.apache.org/thread/bv51zhjookcnfbz8b0xsl9wv78sn0j1p
