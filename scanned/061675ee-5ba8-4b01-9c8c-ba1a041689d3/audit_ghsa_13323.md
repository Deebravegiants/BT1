# [C] Apache InLong Insufficient Session Expiration vulnerability

## Summary
Severity: Critical
Advisory: GHSA-757p-7hp5-pqmr
CVE: CVE-2023-31065
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-757p-7hp5-pqmr
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-dao` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-web` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-service` — affected >=1.4.0 <1.7.0

## Details
Insufficient Session Expiration vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.6.0. 

An old session can be used by an attacker even after the user has been deleted or the password has been changed.

Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7836 or  https://github.com/apache/inlong/pull/7884 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31065
- https://github.com/apache/inlong/pull/7836
- https://github.com/apache/inlong/pull/7884
- https://github.com/apache/inlong
- https://lists.apache.org/thread/to7o0n2cks0omtwo6mhh5cs2vfdbplqf
