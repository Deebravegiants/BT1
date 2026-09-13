# [M] hibernate-validator Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x83m-pf6f-pf9g
CVE: CVE-2023-1932
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-x83m-pf6f-pf9g
Type: github-advisory

## Affected
- Maven: `org.hibernate.validator:hibernate-validator` — affected >=0 <6.2.0.Final
- Maven: `org.hibernate:hibernate-validator` — affected >=0 <6.2.0.Final

## Details
A flaw was found in hibernate-validator's 'isValid' method in the org.hibernate.validator.internal.constraintvalidators.hv.SafeHtmlValidator class, which can be bypassed by omitting the tag ending in a less-than character. Browsers may render an invalid html, allowing HTML injection or Cross-Site-Scripting (XSS) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1932
- https://access.redhat.com/security/cve/CVE-2023-1932
- https://bugzilla.redhat.com/show_bug.cgi?id=1809444
- https://github.com/hibernate/hibernate-validator
