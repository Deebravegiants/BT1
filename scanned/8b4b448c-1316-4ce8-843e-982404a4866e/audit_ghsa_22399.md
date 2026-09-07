# [M] Wildfly Authorization Misconfiguration

## Summary
Severity: Medium
Advisory: GHSA-82v2-f875-73g9
CVE: CVE-2019-14838
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-82v2-f875-73g9
Type: github-advisory

## Affected
- Maven: `org.wildfly.core:wildfly-host-controller` — affected >=0 <7.2.5.GA

## Details
A flaw was found in wildfly-core before 7.2.5.GA. The Management users with Monitor, Auditor and Deployer Roles should not be allowed to modify the runtime state of the server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14838
- https://github.com/wildfly/wildfly-core/pull/3981
- https://github.com/wildfly/wildfly-core/commit/131fa6880ae1523fac9e96df54dc394b63b0eed3
- https://access.redhat.com/errata/RHSA-2019:3082
- https://access.redhat.com/errata/RHSA-2019:3083
- https://access.redhat.com/errata/RHSA-2019:4018
- https://access.redhat.com/errata/RHSA-2019:4019
- https://access.redhat.com/errata/RHSA-2019:4020
- https://access.redhat.com/errata/RHSA-2019:4021
- https://access.redhat.com/errata/RHSA-2019:4040
- https://access.redhat.com/errata/RHSA-2019:4041
- https://access.redhat.com/errata/RHSA-2019:4042
- https://access.redhat.com/errata/RHSA-2019:4045
- https://access.redhat.com/errata/RHSA-2020:0728
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14838
- https://github.com/wildfly/wildfly-core
