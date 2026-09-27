# [M] BIT-wildfly-2021-3503

## Summary
Severity: Medium
Advisory: BIT-wildfly-2021-3503
Aliases: CVE-2021-3503, GHSA-c4r5-xvgw-2942
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-wildfly-2021-3503
Type: osv

## Affected
- Bitnami: `wildfly` — affected >=0 <23.0.1

## Details
A flaw was found in Wildfly where insufficient RBAC restrictions may lead to expose metrics data. The highest threat from this vulnerability is to the confidentiality.

## References
- https://access.redhat.com/security/cve/CVE-2021-3503
- https://bugzilla.redhat.com/show_bug.cgi?id=1942693
- https://github.com/advisories/GHSA-c4r5-xvgw-2942
- https://github.com/wildfly/wildfly/pull/14136
- https://issues.redhat.com/browse/WFLY-11933
- https://nvd.nist.gov/vuln/detail/CVE-2021-3503
