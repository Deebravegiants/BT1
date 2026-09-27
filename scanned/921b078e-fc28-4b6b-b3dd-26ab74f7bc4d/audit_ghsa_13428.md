# [C] Apache InLong Improper Privilege Management vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q5p5-xg93-2jqc
CVE: CVE-2023-31062
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-q5p5-xg93-2jqc
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.2.0 <1.7.0
- Maven: `org.apache.inlong:manager-dao` — affected >=1.2.0 <1.7.0
- Maven: `org.apache.inlong:manager-service` — affected >=1.2.0 <1.7.0
- Maven: `org.apache.inlong:manager-web` — affected >=1.2.0 <1.7.0

## Details
Improper Privilege Management Vulnerabilities in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.2.0 through 1.6.0.  When the attacker has access to a valid (but unprivileged) account, the exploit can be executed using Burp Suite by sending a login request and following it with a subsequent HTTP request using the returned cookie.

Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7836 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31062
- https://github.com/apache/inlong/pull/7836
- https://github.com/apache/inlong
- https://lists.apache.org/thread/btorjbo9o71h22tcvxzy076022hjdzq0
