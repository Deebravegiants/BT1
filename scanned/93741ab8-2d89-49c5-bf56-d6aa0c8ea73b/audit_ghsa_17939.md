# [H] xml2rfc has an arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-cfmv-h8fx-85m7
CVE: CVE-2025-11058
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-cfmv-h8fx-85m7
Type: github-advisory

## Affected
- PyPI: `xml2rfc` — affected >=0 <3.30.1

## Details
### Impact
When generating PDF files, this vulnerability allows an attacker to read arbitrary files from the filesystem by injecting malicious link element into the XML.

### Workarounds
Test untrusted input with `link` elements with `rel="attachment"` before processing.

### Credits
This vulnerability was reported by Mohamed Ouad from [Doyensec](https://doyensec.com/).

## References
- https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-cfmv-h8fx-85m7
- https://github.com/ietf-tools/xml2rfc/commit/f2b245bc0aeeac0667c8f74e976c466c5991f0e4
- https://github.com/ietf-tools/xml2rfc
