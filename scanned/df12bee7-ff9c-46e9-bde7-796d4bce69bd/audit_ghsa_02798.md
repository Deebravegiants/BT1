# [C] Command injection leading to Remote Code Execution in Apache Storm

## Summary
Severity: Critical
Advisory: GHSA-6768-mcjc-8223
CVE: CVE-2021-38294
CWE: CWE-74, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-27
Source: https://github.com/advisories/GHSA-6768-mcjc-8223
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm` — affected >=2.2.0 <2.2.1
- Maven: `org.apache.storm:storm` — affected >=2.0.0 <2.1.1
- Maven: `org.apache.storm:storm` — affected >=1.0.0 <1.2.4

## Details
A Command Injection vulnerability exists in the getTopologyHistory service of the Apache Storm 2.x prior to 2.2.1 and Apache Storm 1.x prior to 1.2.4. A specially crafted thrift request to the Nimbus server allows Remote Code Execution (RCE) prior to authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38294
- https://github.com/apache/storm
- https://lists.apache.org/thread.html/r5fe881f6ca883908b7a0f005d35115af49f43beea7a8b0915e377859%40%3Cuser.storm.apache.org%3E
- https://seclists.org/oss-sec/2021/q4/44
- http://packetstormsecurity.com/files/165019/Apache-Storm-Nimbus-2.2.0-Command-Execution.html
