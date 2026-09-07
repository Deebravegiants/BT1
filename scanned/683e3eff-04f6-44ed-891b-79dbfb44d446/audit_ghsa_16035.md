# [H] powertac-server XML External Entity vulnerability

## Summary
Severity: High
Advisory: GHSA-pgrc-8wp5-5mvq
CVE: CVE-2024-51135
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-11
Source: https://github.com/advisories/GHSA-pgrc-8wp5-5mvq
Type: github-advisory

## Affected
- Maven: `org.powertac:server-interface` — affected >=0

## Details
An XML External Entity (XXE) vulnerability in the component DocumentBuilderFactory of powertac-server v1.9.0 allows attackers to access sensitive information or execute arbitrary code via supplying a crafted request containing malicious XML entities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51135
- https://github.com/powertac/powertac-server/issues/1166
- https://github.com/powertac/powertac-server
- https://mvnrepository.com/artifact/org.powertac/server-interface
