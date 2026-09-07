# [M] Eclipse Jetty Server generates error message containing sensitive information

## Summary
Severity: Medium
Advisory: GHSA-9rgv-h7x4-qw8g
CVE: CVE-2018-12536
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-9rgv-h7x4-qw8g
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.11.v20180605
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.0.0 <9.3.24.v20180605

## Details
In Eclipse Jetty Server, all 9.x versions, on webapps deployed using default Error Handling, when an intentionally bad query arrives that doesn't match a dynamic url-pattern, and is eventually handled by the DefaultServlet's static file serving, the bad characters can trigger a java.nio.file.InvalidPathException which includes the full path to the base resource directory that the DefaultServlet and/or webapp is using. If this InvalidPathException is then handled by the default Error Handler, the InvalidPathException message is included in the error response, revealing the full server path to the requesting system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12536
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=535670
- https://github.com/eclipse/jetty.project
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/05/msg00016.html
- https://security.netapp.com/advisory/ntap-20181014-0001
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03953en_us
- https://web.archive.org/web/20200516001904/http://www.securitytracker.com/id/1041194
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
