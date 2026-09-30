# [H] Wildfly-Core user account mismanagement

## Summary
Severity: High
Advisory: GHSA-p9xf-3rm3-qh2h
CVE: CVE-2021-3717
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-p9xf-3rm3-qh2h
Type: github-advisory

## Affected
- Maven: `org.wildfly.core:wildfly-core-parent` — affected >=0 <17.0

## Details
A flaw was found in Wildfly. An incorrect JBOSS_LOCAL_USER challenge location when using the elytron configuration may lead to JBOSS_LOCAL_USER access to all users on the machine. The highest threat from this vulnerability is to confidentiality, integrity, and availability. This flaw affects wildfly-core versions prior to 17.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3717
- https://bugzilla.redhat.com/show_bug.cgi?id=1991305
- https://security.netapp.com/advisory/ntap-20220804-0002
