# [H] CVE-2020-14061

## Summary
Severity: High
Advisory: CVE-2020-14061
Aliases: GHSA-c2q3-4qrh-fm48
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-14
Source: https://osv.dev/vulnerability/CVE-2020-14061
Type: osv

## Details
FasterXML jackson-databind 2.x before 2.9.10.5 mishandles the interaction between serialization gadgets and typing, related to oracle.jms.AQjmsQueueConnectionFactory, oracle.jms.AQjmsXATopicConnectionFactory, oracle.jms.AQjmsTopicConnectionFactory, oracle.jms.AQjmsXAQueueConnectionFactory, and oracle.jms.AQjmsXAConnectionFactory (aka weblogic/oracle-aqjms).

## References
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://lists.debian.org/debian-lts-announce/2020/07/msg00001.html
- https://security.netapp.com/advisory/ntap-20200702-0003/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://github.com/FasterXML/jackson-databind/issues/2698
