# [C] Deserialization of Untrusted Data leading to Remote Code Execution in Apache Storm

## Summary
Severity: Critical
Advisory: GHSA-w729-7633-2fw5
CVE: CVE-2021-40865
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-27
Source: https://github.com/advisories/GHSA-w729-7633-2fw5
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm` — affected >=2.2.0 <2.2.1
- Maven: `org.apache.storm:storm` — affected >=1.0.0 <1.2.4
- Maven: `org.apache.storm:storm` — affected >=2.1.0 <2.1.1

## Details
An Unsafe Deserialization vulnerability exists in the worker services of the Apache Storm supervisor server allowing pre-auth Remote Code Execution (RCE). Apache Storm 2.2.x users should upgrade to version 2.2.1 or 2.3.0. Apache Storm 2.1.x users should upgrade to version 2.1.1. Apache Storm 1.x users should upgrade to version 1.2.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40865
- https://lists.apache.org/thread.html/r8d45e74299897b6734dd0f788c46a631009ce2eeb731523386f7a253%40%3Cuser.storm.apache.org%3E
- https://seclists.org/oss-sec/2021/q4/45
