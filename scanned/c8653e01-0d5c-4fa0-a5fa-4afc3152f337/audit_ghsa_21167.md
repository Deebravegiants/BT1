# [C] Insufficient user input in Apache Jetspeed-2

## Summary
Severity: Critical
Advisory: GHSA-h975-r69h-4w9p
CVE: CVE-2022-32533
CWE: CWE-352, CWE-611, CWE-79, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-07
Source: https://github.com/advisories/GHSA-h975-r69h-4w9p
Type: github-advisory

## Affected
- Maven: `org.apache.portals.jetspeed-2:jetspeed-commons` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Apache Jetspeed-2 does not sufficiently filter untrusted user input by default leading to a number of issues including XSS, CSRF, XXE, and SSRF. Setting the configuration option "xss.filter.post = true" may mitigate these issues. NOTE: Apache Jetspeed is a dormant project of Apache Portals and no updates will be provided for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32533
- https://lists.apache.org/thread/d3g248pr03x8rvmh8p2t3xdlw0wn5dz2
- https://www.openwall.com/lists/oss-security/2022/07/06/1
- http://www.openwall.com/lists/oss-security/2022/07/06/1
