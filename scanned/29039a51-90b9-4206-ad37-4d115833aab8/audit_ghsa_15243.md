# [H] Apache InLong Manager Arbitrary File Read Vulnerability

## Summary
Severity: High
Advisory: GHSA-crwj-2r3c-gx2g
CVE: CVE-2023-51785
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-crwj-2r3c-gx2g
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.5.0 <1.10.0

## Details
Deserialization of Untrusted Data vulnerability in Apache InLong.This issue affects Apache InLong: from 1.7.0 through 1.9.0, the attackers can make a arbitrary file read attack using mysql driver. Users are advised to upgrade to Apache InLong's 1.10.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/9331

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51785
- https://github.com/apache/inlong/pull/9331
- https://github.com/apache/inlong/commit/d674bfe28416aff728eabafc1f6b8bb9ba5a5b8e
- https://github.com/apache/inlong
- https://lists.apache.org/thread/g0yjmtjqvp8bnf1j0tdsk0nhfozjdjno
- http://www.openwall.com/lists/oss-security/2024/01/03/2
