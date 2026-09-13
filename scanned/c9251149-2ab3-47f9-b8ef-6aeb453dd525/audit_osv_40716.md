# [H] FastGPT: SSRF in HTTP-tool OpenAPI schema importer via SwaggerParser $ref (bypasses the isInternalAddress guard)

## Summary
Severity: High
Advisory: CVE-2026-54607
Aliases: GHSA-72hf-5382-2mq9
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-54607
Type: osv

## Details
FastGPT is a knowledge-based AI application platform. Prior to 4.15.0-beta4, the HTTP-tool OpenAPI schema importer validates only the top-level URL before passing it to SwaggerParser.bundle, whose remote reference resolver fetches $ref URLs without FastGPT's internal-address guard and returns fetched content inline, allowing an authenticated team member to read internal services or cloud metadata. This issue is fixed in version 4.15.0-beta4.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54607.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-72hf-5382-2mq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-54607
- https://github.com/labring/FastGPT/commit/1d7b8768aecd53ae59372fd68b10af0e80722c79
- https://github.com/labring/FastGPT/pull/7073
