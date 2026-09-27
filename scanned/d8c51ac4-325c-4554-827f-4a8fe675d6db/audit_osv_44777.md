# [M] CVE-2026-86144

## Summary
Severity: Medium
Advisory: CVE-2026-86144
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86144
Type: osv

## Details
In xinclude in libxml2 before 2.15.4, xmlXIncludeProcess and xmlXIncludeProcessTree do not propagate parseFlags. This has security relevance for, for example, the XML_PARSE_NONET flag, if (without it) a custom resource loader accesses the internet and triggers XML external entity injection, SSRF, or a denial of service (e.g., for an attacker-controlled internet resource that is intentionally slow).

## References
- https://github.com/GNOME/libxml2/compare/v2.15.3...v2.15.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86144.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86144
- https://github.com/GNOME/libxml2/commit/b63cd517afecb76582dd9488c55e54ceaf50de61
