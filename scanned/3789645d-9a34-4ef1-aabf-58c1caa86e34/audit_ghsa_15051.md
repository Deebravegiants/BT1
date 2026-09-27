# [C] Apache InLong Manager Remote Code Execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9xg9-hh45-xcm6
CVE: CVE-2023-51784
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-9xg9-hh45-xcm6
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.5.0 <1.10.0

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache InLong.This issue affects Apache InLong: from 1.5.0 through 1.9.0, which could lead to Remote Code Execution. Users are advised to upgrade to Apache InLong's 1.10.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/9329

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51784
- https://github.com/apache/inlong/pull/9329
- https://github.com/apache/inlong/commit/1607837be28438c0ccae8da15afb653f2afed090
- https://github.com/apache/inlong
- https://lists.apache.org/thread/4nxbyl6mh5jgh0plk0qposbxwn6w9h8j
- http://www.openwall.com/lists/oss-security/2024/01/03/1
