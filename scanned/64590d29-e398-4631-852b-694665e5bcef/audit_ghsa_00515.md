# [H] UnixAuthenticationService in Apache Ranger was updated to correctly handle user input to avoid Stack-based buffer overflow

## Summary
Severity: High
Advisory: GHSA-c99h-fgqm-6679
CVE: CVE-2018-11778
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-c99h-fgqm-6679
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <1.2.0

## Details
UnixAuthenticationService in Apache Ranger 1.2.0 was updated to correctly handle user input to avoid Stack-based buffer overflow. Versions prior to 1.2.0 should be upgraded to 1.2.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11778
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-c99h-fgqm-6679
- https://lists.apache.org/thread.html/r04bc435a92911de4b52d2b98f169bd7cf2e8bbeb53b03788df8f932c@%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/rd88077a781ef38f7687c100f93992f4dda8aa101925050c4af470998@%3Cdev.ranger.apache.org%3E
- https://seclists.org/oss-sec/2018/q4/11
