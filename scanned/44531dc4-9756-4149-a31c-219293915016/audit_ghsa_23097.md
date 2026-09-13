# [H] MJML vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-4hch-r9xf-6vfr
CVE: CVE-2020-12827
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4hch-r9xf-6vfr
Type: github-advisory

## Affected
- npm: `mjml` — affected >=0 <4.6.3

## Details
MJML prior to 4.6.3 contains a path traversal vulnerability when processing the `mj-include` directive within an MJML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12827
- https://github.com/mjmlio/mjml/commit/30e29ed2cdaec8684d60a6d12ea07b611c765a12
- https://github.com/mjmlio/mjml
- https://github.com/mjmlio/mjml/releases/tag/v4.6.3
- http://packetstormsecurity.com/files/158111/MJML-4.6.2-Path-Traversal.html
- http://seclists.org/fulldisclosure/2020/Jun/23
