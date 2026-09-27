# [C] Pippo RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h892-x453-86wc
CVE: CVE-2018-18240
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h892-x453-86wc
Type: github-advisory

## Affected
- Maven: `ro.pippo:pippo-core` — affected >=0 <1.12.0
- Maven: `ro.pippo:pippo-session` — affected >=0 <1.12.0

## Details
Pippo through 1.11.0 allows remote code execution via a command to java.lang.ProcessBuilder because the XstreamEngine component does not use XStream's available protection mechanisms to restrict unmarshalling.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18240
- https://github.com/pippo-java/pippo/issues/454
- https://github.com/pippo-java/pippo/commit/c6b26551a82d2dd32097fcb17c13c3b830916296
- https://github.com/pippo-java/pippo
