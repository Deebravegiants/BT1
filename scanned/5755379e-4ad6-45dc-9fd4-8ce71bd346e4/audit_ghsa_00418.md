# [C] Critical severity vulnerability that affects org.eclipse.jetty:jetty-server

## Summary
Severity: Critical
Advisory: GHSA-vgg8-72f2-qm23
CVE: CVE-2017-7657
CWE: CWE-190, CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-vgg8-72f2-qm23
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.2.25.v20180606
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.24.v20180605

## Details
In Eclipse Jetty, versions 9.2.x and older, 9.3.x, transfer-encoding chunks are handled poorly. The chunk length parsing was vulnerable to an integer overflow. Thus a large chunk size could be interpreted as a smaller chunk size and content sent as chunk body could be interpreted as a pipelined request. If Jetty was deployed behind an intermediary that imposed some authorization and that intermediary allowed arbitrarily large chunks to be passed on unchanged, then this flaw could be used to bypass the authorization imposed by the intermediary as the fake pipelined request would not be interpreted by the intermediary as a request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7657
- https://access.redhat.com/errata/RHSA-2019:0910
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=535668
- https://github.com/advisories/GHSA-vgg8-72f2-qm23
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r41af10c4adec8d34a969abeb07fd0d6ad0c86768b751464f1cdd23e8@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r9159c9e7ec9eac1613da2dbaddbc15691a13d4dbb2c8be974f42e6ae@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/ra6f956ed4ec2855583b2d0c8b4802b450f593d37b77509b48cd5d574@%3Ccommits.druid.apache.org%3E
- https://security.netapp.com/advisory/ntap-20181014-0001
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03953en_us
- https://www.debian.org/security/2018/dsa-4278
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://www.securitytracker.com/id/1041194
