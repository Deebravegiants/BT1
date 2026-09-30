# [M] CVE-2019-17569

## Summary
Severity: Medium
Advisory: CVE-2019-17569
Aliases: GHSA-767j-jfh2-jvrc
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2019-17569
Type: osv

## Details
The refactoring present in Apache Tomcat 9.0.28 to 9.0.30, 8.5.48 to 8.5.50 and 7.0.98 to 7.0.99 introduced a regression. The result of the regression was that invalid Transfer-Encoding headers were incorrectly processed leading to a possibility of HTTP Request Smuggling if Tomcat was located behind a reverse proxy that incorrectly handled the invalid Transfer-Encoding header in a particular manner. Such a reverse proxy is considered unlikely.

## References
- https://lists.apache.org/thread.html/r7bc994c965a34876bd94d5ff15b4e1e30b6220a15eb9b47c81915b78%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rc31cbabb46cdc58bbdd8519a8f64b6236b2635a3922bbeba0f0e3743%40%3Ccommits.tomee.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00025.html
- https://lists.apache.org/thread.html/r88def002c5c78534674ca67472e035099fbe088813d50062094a1390%40%3Cannounce.tomcat.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/03/msg00006.html
- https://security.netapp.com/advisory/ntap-20200327-0005/
- https://www.debian.org/security/2020/dsa-4673
- https://www.debian.org/security/2020/dsa-4680
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
