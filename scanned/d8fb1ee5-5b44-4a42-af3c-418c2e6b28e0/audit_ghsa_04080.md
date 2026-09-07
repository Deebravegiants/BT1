# [M] Cross-site Scripting in Eclipse Jetty

## Summary
Severity: Medium
Advisory: GHSA-7vx9-xjhr-rw6h
CVE: CVE-2019-10241
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-23
Source: https://github.com/advisories/GHSA-7vx9-xjhr-rw6h
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.2.27.v20190403
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.26.v20190403
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.16.v20190411

## Details
In Eclipse Jetty version 9.2.26 and older, 9.3.25 and older, and 9.4.15 and older, the server is vulnerable to XSS conditions if a remote client USES a specially formatted URL against the DefaultServlet or ResourceHandler that is configured for showing a Listing of directory contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10241
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=546121
- https://lists.apache.org/thread.html/01e004c3f7c7365863a27e7038b7f32dae56ccf3a496b277c9b7f7b6@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/464892b514c029dfc0c8656a93e1c0de983c473df70fdadbd224e09f@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/8bff534863c7aaf09bb17c3d0532777258dd3a5c7ddda34198cc2742@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ac51944aef91dd5006b8510b0bef337adaccfe962fb90e7af9c22db4@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/bcfb37bfba7b3d7e9c7808b5e5a38a98d6bb714d52cf5162bdd48e32@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/d7c4a664a34853f57c2163ab562f39802df5cf809523ea40c97289c1@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/05/msg00016.html
- https://security.netapp.com/advisory/ntap-20190509-0003
- https://www.debian.org/security/2021/dsa-4949
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
