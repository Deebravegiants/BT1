# [H] Apache InLong Incorrect Permission Assignment for Critical Resource Vulnerability

## Summary
Severity: High
Advisory: GHSA-8rjh-3mhm-966q
CVE: CVE-2023-31453
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-8rjh-3mhm-966q
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-service` — affected >=1.2.0 <1.7.0
- Maven: `org.apache.inlong:manager-web` — affected >=1.2.0 <1.7.0

## Details
Incorrect Permission Assignment for Critical Resource Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.2.0 through 1.6.0. The attacker can delete others' subscriptions, even if they are not the owner
of the deleted subscription. Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7949 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31453
- https://github.com/apache/inlong/pull/7949
- https://github.com/apache/inlong
- https://lists.apache.org/thread/9nz8o2skgc5230w276h4w92j0zstnl06
