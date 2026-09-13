# [C] Firecrawl: Arbitrary file read via JSON Schema $ref expansion

## Summary
Severity: Critical
Advisory: CVE-2026-72904
Aliases: GHSA-3p54-jg6f-68r8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72904
Type: osv

## Details
Firecrawl turns entire websites into LLM-ready markdown or structured data. Prior to 2.11.32, a critical arbitrary file read vulnerability exists in Firecrawl's extraction functionality due to unsafe schema dereferencing of user-supplied JSON schemas in apps/api/src/lib/extract/helpers/dereference-schema.ts. The affected code invokes the json-schema-ref-parser dependency with default resolver settings, allowing external and local file references to be resolved during schema processing. An authenticated attacker can supply a malicious schema containing a $ref within default, const, or enum fields that are not traversed by AJV validation. By triggering a dereference error, file contents from the extract worker filesystem may be included in persisted error messages returned through the extraction API, enabling arbitrary file reads and SSRF against internal or external HTTP endpoints. This issue is fixed in version 2.11.32.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72904.json
- https://github.com/firecrawl/firecrawl/security/advisories/GHSA-3p54-jg6f-68r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-72904
- https://github.com/firecrawl/firecrawl/commit/053630fc5203df91b707a6a523e33db5896a1ee8
