# [M] Uncontrolled Resource Consumption in XNIO

## Summary
Severity: Medium
Advisory: GHSA-c738-77x8-wmq5
CVE: CVE-2020-14340
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-c738-77x8-wmq5
Type: github-advisory

## Affected
- Maven: `org.jboss.xnio:xnio-nio` — affected >=3.8.0.Final <3.8.2.Final
- Maven: `org.jboss.xnio:xnio-nio` — affected >=3.6.0 <3.7.9.Final

## Details
A vulnerability was discovered in XNIO where file descriptor leak caused by growing amounts of NIO Selector file handles between garbage collection cycles. It may allow the attacker to cause a denial of service. It affects XNIO versions 3.6.0.Beta1 through 3.8.1.Final.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14340
- https://bugzilla.redhat.com/show_bug.cgi?id=1860218
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
