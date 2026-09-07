# [M] Information Exposure vulnerability in Eclipse Jetty

## Summary
Severity: Medium
Advisory: GHSA-r28m-g6j9-r2h5
CVE: CVE-2019-10246
CWE: CWE-200, CWE-213
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-04-23
Source: https://github.com/advisories/GHSA-r28m-g6j9-r2h5
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.2.0 <9.2.28.v20190418
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.27.v20190418
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.17.v20190418

## Details
In Eclipse Jetty version 9.2.27, 9.3.26, and 9.4.16, the server running on Windows is vulnerable to exposure of the fully qualified Base Resource directory name on Windows to a remote client when it is configured for showing a Listing of directory contents. This information reveal is restricted to only the content in the configured base resource directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10246
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=546576
- https://lists.apache.org/thread.html/bcce5a9c532b386c68dab2f6b3ce8b0cc9b950ec551766e76391caa3@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://security.netapp.com/advisory/ntap-20190509-0003
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
