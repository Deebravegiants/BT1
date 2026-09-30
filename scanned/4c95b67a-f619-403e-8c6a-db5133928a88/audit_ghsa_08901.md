# [H] Apache Atlas has a Code Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-35xx-9xrg-gwhf
CVE: CVE-2026-40563
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-35xx-9xrg-gwhf
Type: github-advisory

## Affected
- Maven: `org.apache.atlas:apache-atlas` — affected >=0.8 <2.5.0

## Details
### Description:
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache Atlas.

Apache Atlas exposes a DSL search endpoint that accepts user-supplied query strings. Attacker can alter Gremlin traversal logic within grammar-allowed characters to access unintended data.


### Affected Version:
This issue affects Apache Atlas: from 0.8-incubating through 2.4.0.


For affected versions >= 2.0.0, the vulnerability is only exploitable when Atlas is deployed with below non-default configuration.


`atlas.dsl.executor.traversal=false`


### Mitigation:
Users are recommended to upgrade to version 2.5.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40563
- https://github.com/apache/atlas
- https://lists.apache.org/thread/vd0oggmqxl2k1skm0z2f9p0plx7jhmfl
- http://www.openwall.com/lists/oss-security/2026/05/03/9
