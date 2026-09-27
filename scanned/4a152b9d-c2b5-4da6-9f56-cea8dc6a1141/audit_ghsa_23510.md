# [C] Improper Access Control in Apache Shiro

## Summary
Severity: Critical
Advisory: GHSA-p836-389h-j692
CVE: CVE-2016-4437
CWE: CWE-284, CWE-321
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p836-389h-j692
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.2.5

## Details
Apache Shiro before 1.2.5, when a cipher key has not been configured for the "remember me" feature, allows remote attackers to execute arbitrary code or bypass intended access restrictions via an unspecified request parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4437
- https://lists.apache.org/thread.html/ef3a800c7d727a00e04b78e2f06c5cd8960f09ca28c9b69d94c3c4c4%40%3Cannouncements.aurora.apache.org%3E
- https://lists.apache.org/thread.html/ef3a800c7d727a00e04b78e2f06c5cd8960f09ca28c9b69d94c3c4c4@%3Cannouncements.aurora.apache.org%3E
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2016-4437
- http://packetstormsecurity.com/files/137310/Apache-Shiro-1.2.4-Information-Disclosure.html
- http://packetstormsecurity.com/files/157497/Apache-Shiro-1.2.4-Remote-Code-Execution.html
- http://rhn.redhat.com/errata/RHSA-2016-2035.html
- http://rhn.redhat.com/errata/RHSA-2016-2036.html
- http://www.securityfocus.com/archive/1/538570/100/0/threaded
- http://www.securityfocus.com/bid/91024
