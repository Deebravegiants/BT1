# [H] Access and integrity issue within Eclipse Jetty

## Summary
Severity: High
Advisory: GHSA-mwcx-532g-8pq3
CVE: CVE-2018-12538
CWE: CWE-384, CWE-6
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-mwcx-532g-8pq3
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.11.v20180605

## Details
In Eclipse Jetty versions 9.4.0 through 9.4.8, when using the optional Jetty provided FileSessionDataStore for persistent storage of HttpSession details, it is possible for a malicious user to access/hijack other HttpSessions and even delete unmatched HttpSessions present in the FileSystem's storage for the FileSessionDataStore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12538
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=536018
- https://github.com/advisories/GHSA-mwcx-532g-8pq3
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://security.netapp.com/advisory/ntap-20181014-0001
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://www.securitytracker.com/id/1041194
