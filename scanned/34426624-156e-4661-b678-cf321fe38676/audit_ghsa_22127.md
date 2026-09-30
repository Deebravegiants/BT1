# [M] Observable Discrepancy in Wildfly Elytron

## Summary
Severity: Medium
Advisory: GHSA-5499-qjvh-6j7w
CVE: CVE-2021-3642
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5499-qjvh-6j7w
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=0 <1.10.14
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=1.11.0 <1.15.5
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=1.16.0 <1.16.1

## Details
A flaw was found in Wildfly Elytron where ScramServer may be susceptible to Timing Attack if enabled. The highest threat of this vulnerability is confidentiality. This flaw affectes Wildfly Elytron versions prior to 1.10.14.Final, prior to 1.15.5.Final and prior to 1.16.1.Final.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3642
- https://bugzilla.redhat.com/show_bug.cgi?id=1981407
