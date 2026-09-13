# [H] Crash in HeaderParser in dicer

## Summary
Severity: High
Advisory: GHSA-wm7h-9275-46v2
CVE: CVE-2022-24434
CWE: CWE-248
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-21
Source: https://github.com/advisories/GHSA-wm7h-9275-46v2
Type: github-advisory

## Affected
- npm: `dicer` — affected >=0
- Maven: `org.webjars.npm:dicer` — affected >=0

## Details
This affects all versions of the package `dicer`. A malicious attacker can send a modified form to the server and crash the Node.js service. A complete denial of service can be achieved by sending the malicious form in a loop.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24434
- https://github.com/mscdex/busboy/issues/250
- https://github.com/mscdex/dicer/pull/22
- https://github.com/mscdex/dicer/commit/b7fca2e93e8e9d4439d8acc5c02f5e54a0112dac
- https://github.com/mscdex/dicer
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2838865
- https://snyk.io/vuln/SNYK-JS-DICER-2311764
