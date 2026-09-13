# [M] Improper Authentication in Hibernate Validator

## Summary
Severity: Medium
Advisory: GHSA-845h-985r-jrqh
CVE: CVE-2014-3558
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-845h-985r-jrqh
Type: github-advisory

## Affected
- Maven: `org.hibernate:hibernate-validator` — affected >=4.1.0 <4.2.1
- Maven: `org.hibernate:hibernate-validator` — affected >=4.3.0 <4.3.2
- Maven: `org.hibernate:hibernate-validator` — affected >=5.0.0 <5.1.2

## Details
ReflectionHelper (org.hibernate.validator.util.ReflectionHelper) in Hibernate Validator 4.1.0 before 4.2.1, 4.3.x before 4.3.2, and 5.x before 5.1.2 allows attackers to bypass Java Security Manager (JSM) restrictions and execute restricted reflection calls via a crafted application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3558
- https://github.com/hibernate/hibernate-validator/commit/2c95d4ea0ef20977be249e31a4a4f4f4f71c945d
- https://github.com/hibernate/hibernate-validator/commit/67fdff14831c035c25e098fe14bd86523d17f726
- https://github.com/hibernate/hibernate-validator/commit/7e7131939a4361a7cad3e77ab89a8462132c561c
- https://github.com/hibernate/hibernate-validator/commit/c489416f699a46859c134796b3ccfea41ef3ce52
- https://github.com/hibernate/hibernate-validator/commit/c9525ca544b1281e2b7c7347e86e87c86dc1dc6e
- https://github.com/hibernate/hibernate-validator/commit/e8c42b689df8c6752d635d02c6518da3fece3870
- https://github.com/hibernate/hibernate-validator/commit/f97c2021a03c825abdeca1692f5be51e77e76a8f
- https://github.com/hibernate/hibernate-validator/commit/fd4eaed7fb930db6a5e4c03742b4b3adcfecc90e
- https://github.com/hibernate/hibernate-validator
- https://github.com/victims/victims-cve-db/blob/master/database/java/2014/3558.yaml
- https://hibernate.atlassian.net/browse/HV-912
- http://rhn.redhat.com/errata/RHSA-2014-1285.html
- http://rhn.redhat.com/errata/RHSA-2014-1286.html
- http://rhn.redhat.com/errata/RHSA-2014-1287.html
- http://rhn.redhat.com/errata/RHSA-2014-1288.html
- http://rhn.redhat.com/errata/RHSA-2015-0125.html
- http://rhn.redhat.com/errata/RHSA-2015-0720.html
