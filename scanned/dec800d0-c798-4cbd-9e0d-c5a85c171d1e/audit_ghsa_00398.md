# [H] Jetty vulnerable to cache poisoning due to inconsistent HTTP request handling (HTTP Request Smuggling)

## Summary
Severity: High
Advisory: GHSA-84q7-p226-4x5w
CVE: CVE-2017-7656
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-84q7-p226-4x5w
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.3.24.v20180605
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.11.v20180605

## Details
Eclipse Jetty, versions 9.2.x and older, 9.3.x (all configurations), and 9.4.x (non-default configuration with RFC2616 compliance enabled), contain an HTTP Request Smuggling Vulnerability that can result in cache poisoning.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7656
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=535667
- https://github.com/advisories/GHSA-84q7-p226-4x5w
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rbf4565a0b63f9c8b07fab29352a97bbffe76ecafed8b8555c15b83c6@%3Cissues.maven.apache.org%3E
- https://security.netapp.com/advisory/ntap-20181014-0001
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03953en_us
- https://www.debian.org/security/2018/dsa-4278
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://www.securitytracker.com/id/1041194
