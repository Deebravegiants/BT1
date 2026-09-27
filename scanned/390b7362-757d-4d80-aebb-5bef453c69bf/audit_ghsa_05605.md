# [C] XDocReport affected by an XML External Entity (XXE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7jc7-g598-2p64
CVE: CVE-2025-65482
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-7jc7-g598-2p64
Type: github-advisory

## Affected
- Maven: `fr.opensagres.xdocreport:fr.opensagres.xdocreport.document` — affected >=0.9.2 <2.0.4

## Details
An XML External Entity (XXE) vulnerability in opensagres XDocReport v0.9.2 to v2.0.3 allows attackers to execute arbitrary code via uploading a crafted .docx file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65482
- https://github.com/opensagres/xdocreport/commit/d9b90ae6c9489dc43f6427ec7b315cab34125332
- https://drive.google.com/drive/folders/1hUyCznpBN7ivo5krmyJ4OQc_q626Hy5q?usp=sharing
- https://github.com/AT190510-Cuong/CVE-2025-65482-XXE-
- https://github.com/opensagres/xdocreport
- https://hackmd.io/@cuongnh/r1B7B8fJ-g
- https://hackmd.io/@cuongnh/rkJPCgSy-l
