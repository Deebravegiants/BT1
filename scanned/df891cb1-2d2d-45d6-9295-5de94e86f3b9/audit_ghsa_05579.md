# [M] Bio-Formats has an XML External Entity (XXE) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fcqj-76g3-q7qm
CVE: CVE-2026-22186
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-fcqj-76g3-q7qm
Type: github-advisory

## Affected
- Maven: `ome:pom-bio-formats` — affected >=0

## Details
Bio-Formats versions up to and including 8.3.0 contain an XML External Entity (XXE) vulnerability in the Leica Microsystems metadata parsing component (e.g., XLEF). The parser uses an insecurely configured DocumentBuilderFactory when processing Leica XML-based metadata files, allowing external entity expansion and external DTD loading. A crafted metadata file can trigger outbound network requests (SSRF), access local system resources where readable, or cause a denial of service during XML parsing.

## References
- https://github.com/ome/bioformats/security/advisories/GHSA-x9vc-qh97-8gjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22186
- https://docs.openmicroscopy.org/bio-formats
- https://github.com/ome/bioformats
- https://seclists.org/fulldisclosure/2026/Jan/6
- https://www.vulncheck.com/advisories/bio-formats-xxe-in-leica-xlef-metadata-parser
