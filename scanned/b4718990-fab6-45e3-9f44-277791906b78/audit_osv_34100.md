# [H] LibreChat exposes arbitrary chats through Meilisearch engine

## Summary
Severity: High
Advisory: CVE-2025-54868
Aliases: GHSA-p5j8-m4wh-ffmw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54868
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. In versions 0.0.6 through 0.7.7-rc1, an exposed testing endpoint allows reading arbitrary chats directly from the Meilisearch engine. The endpoint /api/search/test allows for direct access to stored chats in the Meilisearch engine without proper access control. This results in the ability to read chats from arbitrary users. This issue is fixed in version 0.7.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54868.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-p5j8-m4wh-ffmw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54868
- https://github.com/danny-avila/LibreChat/commit/0e8041bcac616949c42a68dfb8f108ccc4db5151
