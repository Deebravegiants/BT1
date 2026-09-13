# [H] Mosca REDoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-wqg7-vrj7-v82h
CVE: CVE-2018-11615
CWE: CWE-185, CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-31
Source: https://github.com/advisories/GHSA-wqg7-vrj7-v82h
Type: github-advisory

## Affected
- npm: `mosca` — affected >=0 <2.8.2

## Details
This vulnerability allows remote attackers to deny service on vulnerable installations of npm mosca 2.8.1. Authentication is not required to exploit this vulnerability. The specific flaw exists within the processing of topics. A crafted regular expression can cause the broker to crash. An attacker can leverage this vulnerability to deny access to the target system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11615
- https://github.com/advisories/GHSA-wqg7-vrj7-v82h
- https://zerodayinitiative.com/advisories/ZDI-18-583
