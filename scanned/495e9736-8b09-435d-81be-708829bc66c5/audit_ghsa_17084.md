# [M] Cross-Site Request Forgery in Apache Wicket

## Summary
Severity: Medium
Advisory: GHSA-8vvp-525h-cxf9
CVE: CVE-2024-27439
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-19
Source: https://github.com/advisories/GHSA-8vvp-525h-cxf9
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket` — affected >=9.1.0 <9.17.0
- Maven: `org.apache.wicket:wicket` — affected >=10.0.0-M1 <10.0.0

## Details
An error in the evaluation of the fetch metadata headers could allow a bypass of the CSRF protection in Apache Wicket.
This issue affects Apache Wicket: from 9.1.0 through 9.16.0, and the milestone releases for the 10.0 series.
Apache Wicket 8.x does not support CSRF protection via the fetch metadata headers and as such is not affected.

Users are recommended to upgrade to version 9.17.0 or 10.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27439
- https://github.com/apache/wicket
- https://lists.apache.org/thread/o825rvjjtmz3qv21ps5k7m2w9193g1lo
- http://www.openwall.com/lists/oss-security/2024/03/19/2
