# [M] Improper Input Validation in Hibernate Validator

## Summary
Severity: Medium
Advisory: GHSA-rmrm-75hp-phr2
CVE: CVE-2020-10693
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-rmrm-75hp-phr2
Type: github-advisory

## Affected
- Maven: `org.hibernate.validator:hibernate-validator` — affected >=6.1.0.Final <6.1.5.Final
- Maven: `org.hibernate.validator:hibernate-validator` — affected >=0 <6.0.20.Final
- Maven: `org.hibernate:hibernate-validator` — affected >=6.1.0.Final <6.1.5.Final
- Maven: `org.hibernate:hibernate-validator` — affected >=0 <6.0.20.Final

## Details
A flaw was found in Hibernate Validator version 6.1.2.Final. A bug in the message interpolation processor enables invalid EL expressions to be evaluated as if they were valid. This flaw allows attackers to bypass input sanitation (escaping, stripping) controls that developers may have put in place when handling user-controlled data in error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10693
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10693
- https://lists.apache.org/thread.html/rb8dca19a4e52b60dab0ab21e2ff9968d78f4b84e4033824db1dd24b4@%3Cpluto-scm.portals.apache.org%3E
- https://lists.apache.org/thread.html/rd418deda6f0ebe658c2015f43a14d03acb8b8c2c093c5bf6b880cd7c@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/rf9c17c3efc4a376a96e9e2777eee6acf0bec28e2200e4b35da62de4a@%3Cpluto-dev.portals.apache.org%3E
- https://www.ibm.com/support/pages/node/6348216
- https://www.oracle.com/security-alerts/cpuapr2022.html
