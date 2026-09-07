# [H] Apache Sling Engine vulnerable to cross-site scripting (XSS) that can lead to privilege escalation

## Summary
Severity: High
Advisory: GHSA-mg46-f9h5-g27x
CVE: CVE-2022-45064
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-13
Source: https://github.com/advisories/GHSA-mg46-f9h5-g27x
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.engine` — affected >=0 <2.14.0

## Details
The SlingRequestDispatcher doesn't correctly implement the RequestDispatcher API resulting in a generic type of include-based cross-site scripting issues on the Apache Sling level. The vulnerability is exploitable by an attacker that is able to include a resource with specific content-type and control the include path (i.e. writing content). The impact of a successful attack is privilege escalation to administrative power.

Please update to Apache Sling Engine version 2.14.0 or newer and enable the "Check Content-Type overrides" configuration option.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45064
- https://github.com/apache/sling-org-apache-sling-engine
- https://lists.apache.org/thread/hhp611hltby3whk03vx2mv7cmy3vs0ok
- http://www.openwall.com/lists/oss-security/2023/04/18/6
