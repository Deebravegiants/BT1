# [M] Authenticated SQL Injection via nested eager-loading criteria

## Summary
Severity: Medium
Advisory: CVE-2026-79991
Aliases: GHSA-4mgp-5vf2-7c9m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-79991
Type: osv

## Details
Craft CMS GraphQL entry mutation resolvers (saveEntry, deleteEntry) read siteIddirectly from$argumentswithout passing throughArgumentManagerprepareArguments(), which is the function that enforces site-scope filtering via array_intersect against the GraphQL schema’s allowed sites. The query path (ElementResolverprepareElementQuery) correctly calls prepareArguments()`, so queries to unauthorized sites return empty. But mutations bypass this entirely — an attacker with a token scoped to Site A can create, modify, or delete entries in Site B by passing siteId in the mutations argument.

## References
- https://packagist.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79991.json
- https://github.com/craftcms/cms/releases/tag/5.10.13
- https://github.com/craftcms/cms/security/advisories/GHSA-4mgp-5vf2-7c9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-79991
- https://www.hckrt.com/hacktivity/HCKRT-B5BSMM
- https://github.com/craftcms/cms
