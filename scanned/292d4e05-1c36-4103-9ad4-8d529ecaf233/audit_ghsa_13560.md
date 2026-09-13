# [C] Authorization Bypass in Apache InLong

## Summary
Severity: Critical
Advisory: GHSA-rp6x-ggw6-8g56
CVE: CVE-2023-43668
CWE: CWE-502, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-16
Source: https://github.com/advisories/GHSA-rp6x-ggw6-8g56
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.9.0

## Details
Authorization Bypass Through User-Controlled Key vulnerability in Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.8.0, 

some sensitive params  checks will be bypassed, like "autoDeserizalize","allowLoadLocalInfile"....

.  

Users are advised to upgrade to Apache InLong's 1.9.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/8604

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43668
- https://github.com/apache/inlong/pull/8604
- https://github.com/apache/inlong/commit/46c4e96a84839bd540f47c659c9d8576e393da02
- https://github.com/apache/inlong
- https://lists.apache.org/thread/16gtk7rpdm1rof075ro83fkrnhbzn5sh
