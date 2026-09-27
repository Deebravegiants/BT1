# [C] Apache Shiro vulnerable to a specially crafted HTTP request causing an authentication bypass

## Summary
Severity: Critical
Advisory: GHSA-f6jp-j6w3-w9hm
CVE: CVE-2021-41303
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-f6jp-j6w3-w9hm
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.8.0

## Details
Apache Shiro before 1.8.0, when using Apache Shiro with Spring Boot, a specially crafted HTTP request may cause an authentication bypass. Users should update to Apache Shiro 1.8.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41303
- https://lists.apache.org/thread.html/raae98bb934e4bde304465896ea02d9798e257e486d04a42221e2c41b@%3Cuser.shiro.apache.org%3E
- https://lists.apache.org/thread.html/re470be1ffea44bca28ccb0e67a4cf5d744e2d2b981d00fdbbf5abc13%40%3Cannounce.shiro.apache.org%3E
- https://security.netapp.com/advisory/ntap-20220609-0001
- https://www.oracle.com/security-alerts/cpujul2022.html
