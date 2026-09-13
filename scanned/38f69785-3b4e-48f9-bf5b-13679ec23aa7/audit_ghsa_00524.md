# [C] Policy resource matcher in Apache Ranger before 0.7.1 ignores characters after '' wildcard character

## Summary
Severity: Critical
Advisory: GHSA-758m-6g3q-g3hh
CVE: CVE-2017-7676
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-758m-6g3q-g3hh
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.7.1

## Details
Policy resource matcher in Apache Ranger before 0.7.1 ignores characters after '*' wildcard character - like my*test, test*.txt. This can result in unintended behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7676
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-758m-6g3q-g3hh
- http://www.securityfocus.com/bid/98958
