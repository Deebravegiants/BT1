# [M] Jetty Utility Servlets ConcatServlet Double Decoding Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gwcr-j4wh-j3cq
CVE: CVE-2021-28169
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-gwcr-j4wh-j3cq
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=0 <9.4.41
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=10.0.0 <10.0.3
- Maven: `org.eclipse.jetty:jetty-servlets` — affected >=11.0.0 <11.0.3

## Details
Requests to the `ConcatServlet` and `WelcomeFilter` are able to access protected resources within the `WEB-INF` directory. For example a request to the `ConcatServlet` with a URI of `/concat?/%2557EB-INF/web.xml` can retrieve the web.xml file. This can reveal sensitive information regarding the implementation of a web application.

This occurs because both `ConcatServlet` and `WelcomeFilter` decode the supplied path to verify it is not within the `WEB-INF` or `META-INF` directories. It then uses this decoded path to call `RequestDispatcher` which will also do decoding of the path. This double decoding allows paths with a doubly encoded `WEB-INF` to bypass this security check.

### Impact
This affects all versions of `ConcatServlet` and `WelcomeFilter` in versions before 9.4.41, 10.0.3 and 11.0.3.

### Workarounds

If you cannot update to the latest version of Jetty, you can instead deploy your own version of the [`ConcatServlet`](https://github.com/eclipse/jetty.project/blob/4204526d2fdad355e233f6bf18a44bfe028ee00b/jetty-servlets/src/main/java/org/eclipse/jetty/servlets/ConcatServlet.java) and/or the [`WelcomeFilter`](https://github.com/eclipse/jetty.project/blob/4204526d2fdad355e233f6bf18a44bfe028ee00b/jetty-servlets/src/main/java/org/eclipse/jetty/servlets/WelcomeFilter.java) by using the code from the latest version of Jetty.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-gwcr-j4wh-j3cq
- https://nvd.nist.gov/vuln/detail/CVE-2021-28169
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.debian.org/security/2021/dsa-4949
- https://security.netapp.com/advisory/ntap-20210727-0009
- https://lists.debian.org/debian-lts-announce/2021/06/msg00017.html
- https://lists.apache.org/thread.html/rfff6ff8ffb31e8a32619c79774def44b6ffbb037c128c5ad3eab7171@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf36f1114e84a3379b20587063686148e2d5a39abc0b8a66ff2a9087a@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ref1c161a1621504e673f9197b49e6efe5a33ce3f0e6d8f1f804fc695@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rddbb4f8d5db23265bb63d14ef4b3723b438abc1589f877db11d35450@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rd5b52362f5edf98e0dcab6541a381f571cccc05ad9188e793af688f3@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbefa055282d52d6b58d29a79fbb0be65ab0a38d25f00bd29eaf5e6fd@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb1292d30462b9baedea7c5d9594fc75990d9aa0ec223b48054ca9c25@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r91e34ff61aff8fd25a3f2a21539597c6ef7589a31c199b0a9546477c@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r8a1a332899a1f92c8118b0895b144b27a78e3f25b9d58a34dd5eb084@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r67c4f90658fde875521c949448c54c98517beecdc7f618f902c620ec@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r33eb06b05afbc7df28d31055cae0cb3fd36cab808c884bf6d680bea5@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r32b0b640ad2be3b858f0af51c68a7d5c5a66a462c8bbb93699825cd3@%3Cissues.zookeeper.apache.org%3E
