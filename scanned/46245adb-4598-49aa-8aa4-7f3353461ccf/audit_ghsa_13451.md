# [C] Apache InLong has Weak Password Requirements in Apache InLong

## Summary
Severity: Critical
Advisory: GHSA-w3wr-gmwf-r333
CVE: CVE-2023-31098
CWE: CWE-521
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-w3wr-gmwf-r333
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.1.0 <1.47.0

## Details
Weak Password Requirements vulnerability in Apache Software Foundation Apache InLong. This issue affects Apache InLong from 1.1.0 through 1.6.0. When users change their password to a simple password (with any character or symbol), attackers can easily guess the user's password and access the account. Users are advised to upgrade to Apache InLong 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7805 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31098
- https://github.com/apache/inlong/pull/7805
- https://github.com/apache/inlong
- https://lists.apache.org/thread/1fvloc3no1gbffzrcsx9ltsg08wr2d1w
