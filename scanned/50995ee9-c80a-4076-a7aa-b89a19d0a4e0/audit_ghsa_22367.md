# [H] Apache Wicket vulnerable to CSRF attacks

## Summary
Severity: High
Advisory: GHSA-xc66-mg8r-q6r5
CVE: CVE-2016-6806
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xc66-mg8r-q6r5
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=6.20.0 <6.25.0
- Maven: `org.apache.wicket:wicket-core` — affected >=7.0.0 <7.5.0
- Maven: `org.apache.wicket:wicket-core` — affected >=8.0.0-M1 <8.0.0-M2

## Details
Apache Wicket 6.x before 6.25.0, 7.x before 7.5.0, and 8.0.0-M1 provide a CSRF prevention measure that fails to discover some cross origin requests. The mitigation is to not only check the Origin HTTP header, but also take the Referer HTTP header into account when no Origin was provided. Furthermore, not all Wicket server side targets were subjected to the CSRF check. This was also fixed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6806
- https://github.com/apache/wicket
- https://lists.apache.org/thread.html/074b72585f4b7c6adda1af52aecbfe1be23c6d6f5bb9382270f059cd@%3Cannounce.apache.org%3E
