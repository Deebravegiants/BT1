# [M] @cyntler/react-doc-viewer's TXTRenderer fails to sanitize file content and explicitly casts raw data as a ReactNode

## Summary
Severity: Medium
Advisory: GHSA-fvhg-p4hf-79x3
CVE: CVE-2026-30691
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-fvhg-p4hf-79x3
Type: github-advisory

## Affected
- npm: `@cyntler/react-doc-viewer` — affected >=0

## Details
Cross-Site Scripting (XSS) vulnerability in @cyntler/react-doc-viewer v1.17.1 allows remote attackers to execute arbitrary JavaScript via a crafted .txt file. The TXTRenderer component fails to sanitize file content and explicitly casts raw data as a ReactNode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30691
- https://github.com/cyntler/react-doc-viewer/issues/317
- https://github.com/cyntler/react-doc-viewer
- https://github.com/walidriouah/CVE-2026-30691
