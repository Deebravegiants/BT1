# [H] Apache Sling Authentication Service vulnerability

## Summary
Severity: High
Advisory: GHSA-vcvp-89fq-hwj8
CVE: CVE-2017-15700
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vcvp-89fq-hwj8
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.auth.core` — affected >=1.4.0 <1.4.2

## Details
A flaw in the org.apache.sling.auth.core.AuthUtil#isRedirectValid method in Apache Sling Authentication Service 1.4.0 allows an attacker, through the Sling login form, to trick a victim to send over their credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15700
- https://github.com/apache/sling-org-apache-sling-auth-core
- https://lists.apache.org/thread.html/182bed1dd6933824a81cc5f07639eeb813fbd8f2cc49d51b452ab621@%3Cdev.sling.apache.org%3E
