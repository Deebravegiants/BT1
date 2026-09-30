# [M] Uncontrolled Resource Consumption in WildFly

## Summary
Severity: Medium
Advisory: GHSA-97hp-6q9g-5cw2
CVE: CVE-2020-25689
CWE: CWE-400, CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-97hp-6q9g-5cw2
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-dist` — affected >=0 <21.0.1

## Details
A memory leak flaw was found in WildFly in all versions up to 21.0.0.Final, where host-controller tries to reconnect in a loop, generating new connections which are not properly closed while not able to connect to domain-controller. This flaw allows an attacker to cause an Out of memory (OOM) issue, leading to a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25689
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-25689
- https://security.netapp.com/advisory/ntap-20201123-0006
