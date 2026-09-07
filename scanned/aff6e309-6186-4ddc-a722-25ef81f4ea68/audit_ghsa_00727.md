# [H] Privilege Escalation in Hibernate Validator

## Summary
Severity: High
Advisory: GHSA-xxgp-pcfc-3vgc
CVE: CVE-2017-7536
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-xxgp-pcfc-3vgc
Type: github-advisory

## Affected
- Maven: `org.hibernate:hibernate-validator` — affected >=5.2.0 <5.2.5.Final
- Maven: `org.hibernate:hibernate-validator` — affected >=5.3.0 <5.3.6.Final
- Maven: `org.hibernate:hibernate-validator` — affected >=5.4.0 <5.4.2.Final

## Details
In Hibernate Validator 5.2.x before 5.2.5.Final, 5.3.x before 5.3.6.Final, and 5.4.x before 5.4.2.Final, it was found that when the security manager's reflective permissions, which allows it to access the private members of the class, are granted to Hibernate Validator, a potential privilege escalation can occur. By allowing the calling code to access those private members without the permission an attacker may be able to validate an invalid instance and access the private member value via ConstraintViolation#getInvalidValue().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7536
- https://github.com/hibernate/hibernate-validator/commit/0886e89900d343ea20fde5137c9a3086e6da9ac
- https://github.com/hibernate/hibernate-validator/commit/0778a5c98b817771a645c6f4ba0b28dd8b5437b
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://github.com/hibernate/hibernate-validator
- https://bugzilla.redhat.com/show_bug.cgi?id=1465573
- https://access.redhat.com/errata/RHSA-2018:3817
- https://access.redhat.com/errata/RHSA-2018:2927
- https://access.redhat.com/errata/RHSA-2018:2743
- https://access.redhat.com/errata/RHSA-2018:2742
- https://access.redhat.com/errata/RHSA-2018:2741
- https://access.redhat.com/errata/RHSA-2018:2740
- https://access.redhat.com/errata/RHSA-2017:3458
- https://access.redhat.com/errata/RHSA-2017:3456
- https://access.redhat.com/errata/RHSA-2017:3455
- https://access.redhat.com/errata/RHSA-2017:3454
- https://access.redhat.com/errata/RHSA-2017:3141
- https://access.redhat.com/errata/RHSA-2017:2811
- https://access.redhat.com/errata/RHSA-2017:2810
- https://access.redhat.com/errata/RHSA-2017:2809
