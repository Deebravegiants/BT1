# [H] SQL injection vulnerability in the policy admin tool in Apache Ranger

## Summary
Severity: High
Advisory: GHSA-4rjf-mxfm-98h5
CVE: CVE-2016-2174
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-4rjf-mxfm-98h5
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.5.3

## Details
SQL injection vulnerability in the policy admin tool in Apache Ranger before 0.5.3 allows remote authenticated administrators to execute arbitrary SQL commands via the eventTime parameter to service/plugins/policies/eventTime.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2174
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-4rjf-mxfm-98h5
- http://www.openwall.com/lists/oss-security/2016/06/01/3
