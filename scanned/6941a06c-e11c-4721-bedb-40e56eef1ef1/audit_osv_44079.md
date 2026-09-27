# [M] NLTK before 3.10.3 Entity Expansion DoS via ElementTree

## Summary
Severity: Medium
Advisory: CVE-2026-78681
Aliases: GHSA-97qj-x29f-37w7, PYSEC-2026-3748
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78681
Type: osv

## Details
NLTK versions before 3.10.3 use xml.etree.ElementTree to parse XML in multiple modules, which honors entity declarations in document DTDs. Attackers can craft XML payloads with nested entity declarations that expand from hundreds of bytes to megabytes in memory, causing denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78681.json
- https://github.com/nltk/nltk/security/advisories/GHSA-97qj-x29f-37w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-78681
- https://www.vulncheck.com/advisories/nltk-before-entity-expansion-dos-via-elementtree
