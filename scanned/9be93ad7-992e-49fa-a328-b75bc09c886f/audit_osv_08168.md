# [H] CVE-2016-1181

## Summary
Severity: High
Advisory: CVE-2016-1181
Aliases: GHSA-7jw3-5q4w-89qg
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-04
Source: https://osv.dev/vulnerability/CVE-2016-1181
Type: osv

## Details
ActionServlet.java in Apache Struts 1 1.x through 1.3.10 mishandles multithreaded access to an ActionForm instance, which allows remote attackers to execute arbitrary code or cause a denial of service (unexpected memory access) via a multipart request, a related issue to CVE-2015-0899.

## References
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://jvn.jp/en/jp/JVN03188560/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000096
- http://www.securityfocus.com/bid/91068
- http://www.securityfocus.com/bid/91787
- http://www.securitytracker.com/id/1036056
- https://security-tracker.debian.org/tracker/CVE-2016-1181
- https://security.netapp.com/advisory/ntap-20180629-0006/
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1343538
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://github.com/kawasima/struts1-forever/commit/eda3a79907ed8fcb0387a0496d0cb14332f250e8
