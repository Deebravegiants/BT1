# [H] BIT-modsecurity-2021-42717

## Summary
Severity: High
Advisory: BIT-modsecurity-2021-42717
Aliases: BIT-modsecurity2-2021-42717, CVE-2021-42717
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-modsecurity-2021-42717
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=2.0.0 <2.9.5

## Details
ModSecurity 3.x through 3.0.5 mishandles excessively nested JSON objects. Crafted JSON objects with nesting tens-of-thousands deep could result in the web server being unable to service legitimate requests. Even a moderately large (e.g., 300KB) HTTP request can occupy one of the limited NGINX worker processes for minutes and consume almost all of the available CPU on the machine. Modsecurity 2 is similarly vulnerable: the affected versions include 2.8.0 through 2.9.4.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00042.html
- https://www.debian.org/security/2021/dsa-5023
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/modsecurity-dos-vulnerability-in-json-parsing-cve-2021-42717/
- https://nvd.nist.gov/vuln/detail/CVE-2021-42717
