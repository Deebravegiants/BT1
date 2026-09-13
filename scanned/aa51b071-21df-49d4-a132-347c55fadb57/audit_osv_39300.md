# [M] Symfony: XXE (Local File Disclosure) in DomCrawler::addXmlContent() via validateOnParse = true

## Summary
Severity: Medium
Advisory: CVE-2026-45071
Aliases: GHSA-x6g4-fwcc-jj8w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-45071
Type: osv

## Details
Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.52, 6.4.40, 7.4.12, and 8.0.12, Crawler::addXmlContent() set DOMDocument::$validateOnParse = true before loadXML(), re-enabling external entity resolution and allowing attacker-supplied XML to expand file:// entities such as local files. This issue is fixed in versions 5.4.52, 6.4.40, 7.4.12, and 8.0.12.

## References
- https://github.com/symfony/symfony/releases/tag/v5.4.52
- https://github.com/symfony/symfony/releases/tag/v6.4.40
- https://github.com/symfony/symfony/releases/tag/v7.4.12
- https://github.com/symfony/symfony/releases/tag/v8.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45071.json
- https://github.com/symfony/symfony/security/advisories/GHSA-x6g4-fwcc-jj8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-45071
- https://github.com/symfony/symfony/commit/eea5fd7488cbdc241da4ce242344b7d9a3ecdf3d
