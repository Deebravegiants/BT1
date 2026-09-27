# [H] In blynk-server a Directory Traversal exists

## Summary
Severity: High
Advisory: GHSA-4r64-wf76-c53p
CVE: CVE-2018-17785
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-4r64-wf76-c53p
Type: github-advisory

## Affected
- Maven: `com.github.blynkkk:blynk-server` — affected >=0 <0.39.7

## Details
In blynk-server in Blynk before 0.39.7, Directory Traversal exists via a ../ in a URI that has /static or /static/js at the beginning, as demonstrated by reading the /etc/passwd file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17785
- https://github.com/blynkkk/blynk-server/issues/1256
- https://github.com/advisories/GHSA-4r64-wf76-c53p
- https://github.com/blynkkk/blynk-server
- https://github.com/blynkkk/blynk-server/releases/tag/v0.39.7
