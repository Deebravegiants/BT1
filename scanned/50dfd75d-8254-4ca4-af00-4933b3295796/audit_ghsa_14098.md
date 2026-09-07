# [M] User data exposure in Apache InLong

## Summary
Severity: Medium
Advisory: GHSA-h79m-5cm2-278c
CVE: CVE-2023-31101
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-h79m-5cm2-278c
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-dao` — affected >=1.5.0 <1.7.0
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.5.0 <1.7.0
- Maven: `org.apache.inlong:manager-service` — affected >=1.5.0 <1.7.0
- Maven: `org.apache.inlong:manager-web` — affected >=1.5.0 <1.7.0

## Details
Insecure Default Initialization of Resource Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.5.0 through 1.6.0.  Users registered in InLong who joined later can see deleted users' data. Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick  https://github.com/apache/inlong/pull/7836 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31101
- https://github.com/apache/inlong/pull/7836
- https://github.com/apache/inlong
- https://lists.apache.org/thread/shvwwr6toqz5rr39rwh4k03z08sh9jmr
