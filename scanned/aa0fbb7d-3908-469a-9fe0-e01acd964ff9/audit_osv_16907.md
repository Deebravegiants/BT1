# [H] CVE-2020-10672

## Summary
Severity: High
Advisory: CVE-2020-10672
Aliases: GHSA-95cm-88f5-f2c7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-18
Source: https://osv.dev/vulnerability/CVE-2020-10672
Type: osv

## Details
FasterXML jackson-databind 2.x before 2.9.10.4 mishandles the interaction between serialization gadgets and typing, related to org.apache.aries.transaction.jms.internal.XaPooledConnectionFactory (aka aries.transaction.jms).

## References
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://lists.debian.org/debian-lts-announce/2020/03/msg00027.html
- https://security.netapp.com/advisory/ntap-20200403-0002/
- https://github.com/FasterXML/jackson-databind/issues/2659
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
