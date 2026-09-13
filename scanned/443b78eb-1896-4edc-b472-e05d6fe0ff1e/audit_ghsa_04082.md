# [M] Installation information leak in Eclipse Jetty

## Summary
Severity: Medium
Advisory: GHSA-xc67-hjx6-cgg6
CVE: CVE-2019-10247
CWE: CWE-200, CWE-213
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-04-23
Source: https://github.com/advisories/GHSA-xc67-hjx6-cgg6
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=7.0.0 <9.2.28.v20190418
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.27.v20190418
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.17.v20190418

## Details
In Eclipse Jetty version 7.x, 8.x, 9.2.27 and older, 9.3.26 and older, and 9.4.16 and older, the server running on any OS and Jetty version combination will reveal the configured fully qualified directory base resource location on the output of the 404 error for not finding a Context that matches the requested path. The default server behavior on jetty-distribution and jetty-home will include at the end of the Handler tree a DefaultHandler, which is responsible for reporting this 404 error, it presents the various configured contexts as HTML for users to click through to. This produced HTML includes output that contains the configured fully qualified directory base resource location for each context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10247
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.debian.org/security/2021/dsa-4949
- https://security.netapp.com/advisory/ntap-20190509-0003
- https://lists.debian.org/debian-lts-announce/2021/05/msg00016.html
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/bcce5a9c532b386c68dab2f6b3ce8b0cc9b950ec551766e76391caa3@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/ac51944aef91dd5006b8510b0bef337adaccfe962fb90e7af9c22db4@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=546577
