# [C] RCE in H2 Console

## Summary
Severity: Critical
Advisory: GHSA-h376-j262-vhq6
CVE: CVE-2021-42392
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-h376-j262-vhq6
Type: github-advisory

## Affected
- Maven: `com.h2database:h2` — affected >=1.1.100 <2.0.206

## Details
### Impact
H2 Console in versions since 1.1.100 (2008-10-14) to 2.0.204 (2021-12-21) inclusive allows loading of custom classes from remote servers through JNDI.

H2 Console doesn't accept remote connections by default. If remote access was enabled explicitly and some protection method (such as security constraint) wasn't set, an intruder can load own custom class and execute its code in a process with H2 Console (H2 Server process or a web server with H2 Console servlet).

It is also possible to load them by creation a linked table in these versions, but it requires `ADMIN` privileges and user with `ADMIN` privileges has full access to the Java process by design. These privileges should never be granted to untrusted users.

### Patches
Since version 2.0.206 H2 Console and linked tables explicitly forbid attempts to specify LDAP URLs for JNDI. Only local data sources can be used.

### Workarounds
H2 Console should never be available to untrusted users.

`-webAllowOthers` is a dangerous setting that should be avoided.

H2 Console Servlet deployed on a web server can be protected with a security constraint:
https://h2database.com/html/tutorial.html#usingH2ConsoleServlet
If `webAllowOthers` is specified, you need to uncomment and edit `<security-role>` and `<security-constraint>` as necessary. See documentation of your web server for more details.

### References
This issue was found and privately reported to H2 team by [JFrog Security](https://www.jfrog.com/)'s vulnerability research team with detailed information.

## References
- https://github.com/h2database/h2database/security/advisories/GHSA-h376-j262-vhq6
- https://nvd.nist.gov/vuln/detail/CVE-2021-42392
- https://github.com/h2database/h2database
- https://github.com/h2database/h2database/releases/tag/version-2.0.206
- https://jfrog.com/blog/the-jndi-strikes-back-unauthenticated-rce-in-h2-database-console
- https://lists.debian.org/debian-lts-announce/2022/02/msg00017.html
- https://security.netapp.com/advisory/ntap-20220119-0001
- https://www.debian.org/security/2022/dsa-5076
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.secpod.com/blog/log4shell-critical-remote-code-execution-vulnerability-in-h2database-console
