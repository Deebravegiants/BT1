# [M] Insufficient Verification of Data Authenticity in Apache InLong

## Summary
Severity: Medium
Advisory: GHSA-wj6q-chpv-mcrx
CVE: CVE-2023-43666
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-16
Source: https://github.com/advisories/GHSA-wj6q-chpv-mcrx
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:inlong` — affected >=1.4.0 <1.9.0

## Details
Insufficient Verification of Data Authenticity vulnerability in Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.8.0, 

General user can view all user data like Admin account.

Users are advised to upgrade to Apache InLong's 1.9.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/8623

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43666
- https://github.com/apache/inlong/pull/8623
- https://lists.apache.org/thread/scbgh3ty3xcxm3q33r2t9f42gwwo1why
