# [H] Hibernate vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-2p5w-cvg5-gc5c
CVE: CVE-2026-0603
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-2p5w-cvg5-gc5c
Type: github-advisory

## Affected
- Maven: `org.hibernate:hibernate-core` — affected >=5.2.8

## Details
A flaw was found in Hibernate. A remote attacker with low privileges could exploit a second-order SQL injection vulnerability by providing specially crafted, unsanitized non-alphanumeric characters in the ID column when the InlineIdsOrClauseBuilder is used. This could lead to sensitive information disclosure, such as reading system files, and allow for data manipulation or deletion within the application's database, resulting in an application level denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0603
- https://access.redhat.com/errata/RHSA-2026:4915
- https://access.redhat.com/errata/RHSA-2026:4916
- https://access.redhat.com/errata/RHSA-2026:4917
- https://access.redhat.com/errata/RHSA-2026:4924
- https://access.redhat.com/errata/RHSA-2026:6011
- https://access.redhat.com/errata/RHSA-2026:6012
- https://access.redhat.com/security/cve/CVE-2026-0603
- https://bugzilla.redhat.com/show_bug.cgi?id=2427147
- https://github.com/hibernate/hibernate-orm
