# [M] Wildfly EJB Client causes DoS

## Summary
Severity: Medium
Advisory: GHSA-qcch-9268-59jw
CVE: CVE-2020-14297
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qcch-9268-59jw
Type: github-advisory

## Affected
- Maven: `org.jboss:jboss-ejb-client` — affected >=0 <4.0.34.Final

## Details
A flaw was discovered in Wildfly's EJB Client as shipped with Red Hat JBoss EAP 7, where some specific EJB transaction objects may get accumulated over the time and can cause services to slow down and eventually unavailable. An attacker can take advantage and cause denial of service attack and make services unavailable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14297
- https://github.com/wildfly/jboss-ejb-client/commit/e5f8e4b591f1698a53adc7e430584ca2a8fc9f1b
- https://github.com/wildfly/jboss-ejb-client/commits/4.0.34.Final
- https://github.com/wildfly/jboss-ejb-client
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14297
- https://bugzilla.redhat.com/show_bug.cgi?id=1853595
- https://access.redhat.com/solutions/21906
- https://access.redhat.com/security/cve/CVE-2020-14297
- https://access.redhat.com/errata/RHSA-2021:3140
- https://access.redhat.com/errata/RHSA-2020:3817
- https://access.redhat.com/errata/RHSA-2020:3642
- https://access.redhat.com/errata/RHSA-2020:3639
- https://access.redhat.com/errata/RHSA-2020:3638
- https://access.redhat.com/errata/RHSA-2020:3637
- https://access.redhat.com/errata/RHSA-2020:3539
- https://access.redhat.com/errata/RHSA-2020:3501
- https://access.redhat.com/errata/RHSA-2020:3464
- https://access.redhat.com/errata/RHSA-2020:3463
- https://access.redhat.com/errata/RHSA-2020:3462
- https://access.redhat.com/errata/RHSA-2020:3461
