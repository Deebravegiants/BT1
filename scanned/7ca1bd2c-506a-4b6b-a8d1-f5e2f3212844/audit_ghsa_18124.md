# [H] xml2rfc is vulnerable to arbitrary file reads through prepped files

## Summary
Severity: High
Advisory: GHSA-9mv7-3c64-mmqw
CVE: CVE-2025-11059
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-9mv7-3c64-mmqw
Type: github-advisory

## Affected
- PyPI: `xml2rfc` — affected >=0 <3.30.2

## Details
### Impact

When generating PDF files, this vulnerability allows an attacker to read arbitrary files from the filesystem by injecting malicious link element into the prepped RFCXML.

### Workarounds

Test untrusted input with `link` elements with `rel="attachment"` before processing.

### References
This is related to [GHSA-cfmv-h8fx-85m7](https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-cfmv-h8fx-85m7).

## References
- https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-9mv7-3c64-mmqw
- https://github.com/ietf-tools/xml2rfc/commit/73fb1c91fc62ac540bb6bd24f982f2becf84c1b0
- https://github.com/ietf-tools/xml2rfc
- https://github.com/ietf-tools/xml2rfc/releases/tag/v3.30.2
