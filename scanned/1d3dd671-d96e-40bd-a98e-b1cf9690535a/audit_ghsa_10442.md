# [M] nbconvert has an Arbitrary File Read via Path Traversal in HTMLExporter Image Embedding

## Summary
Severity: Medium
Advisory: GHSA-7jqv-fw35-gmx9
CVE: CVE-2026-39378
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-7jqv-fw35-gmx9
Type: github-advisory

## Affected
- PyPI: `nbconvert` — affected >=6.5.0 <7.17.1

## Details
## Summary

When `HTMLExporter.embed_images=True`, nbconvert's markdown renderer allows arbitrary file read via path traversal in image references. A malicious notebook can exfiltrate sensitive files from the conversion host by embedding them as base64 data URIs in the output HTML.

## Patches

Upgrade to nbconvert 7.17.1

## Workarounds

Do not enable `HTMLExporter.embed_images` (it is not enabled by default).

## References
- https://github.com/jupyter/nbconvert/security/advisories/GHSA-7jqv-fw35-gmx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39378
- https://github.com/jupyter/nbconvert
- https://github.com/jupyter/nbconvert/releases/tag/v7.17.1
