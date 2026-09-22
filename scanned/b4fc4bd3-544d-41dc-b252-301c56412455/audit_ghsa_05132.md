# [H] Docling: Unsafe XML Entity Expansion in USPTO Patent Backend

## Summary
Severity: High
Advisory: GHSA-m88r-rg27-5xfg
CVE: CVE-2026-44020
CWE: CWE-611, CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-m88r-rg27-5xfg
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=2.13.0 <2.74.0

## Details
### Impact
The USPTO patent XML parser used the standard `xml.sax.parseString()` without protection against XML External Entity (XXE) attacks. An attacker could craft malicious USPTO patent XML files with external entity references that could:
- Read arbitrary files from the server filesystem
- Perform Server-Side Request Forgery (SSRF) attacks
- Cause denial of service through entity expansion (Billion Laughs attack)

The vulnerability affects three USPTO patent format parsers: ICE (v4.x), Grant v2.5, and Application v1.x.

### Patches
Fixed in version 2.74.0. The parser now uses `defusedxml.sax.make_parser()` with secure configuration that blocks external entity resolution (`feature_external_ges=False`, `feature_external_pes=False`) while allowing DTD declarations required by USPTO files. This prevents XXE attacks while maintaining compatibility with the USPTO XML format.

### Workarounds
Avoid processing USPTO patent XML files from untrusted sources. Implement resource limits (memory, CPU time) when processing patent documents.

### References
- Fix release: [v2.74.0](https://github.com/docling-project/docling/releases/tag/v2.74.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-m88r-rg27-5xfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44020
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/security/cve/CVE-2026-44020
- https://bugzilla.redhat.com/show_bug.cgi?id=2492456
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.74.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-240.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44020.json
