# [H] FastGPT: /api/core/chat/record/getCollectionQuote can disclose cross-tenant dataset text due to an unbound initialId lookup

## Summary
Severity: High
Advisory: CVE-2026-61644
Aliases: GHSA-mmg6-2g54-j896
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61644
Type: osv

## Details
FastGPT is a knowledge-based AI application platform. From 4.14.17 until 4.15.0-beta5, the POST /api/core/chat/record/getCollectionQuote endpoint authenticates the caller's chat and collection context, but the initialId center-node lookup is not bound to that authorized context. A low-privileged tenant user can call the endpoint with valid attacker-owned appId, chatId, chatItemDataId, and collectionId values while supplying another tenant's dataset data id as initialId, causing the response to include foreign dataset quote or full-text content. This issue is fixed in version 4.15.0-beta5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61644.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-mmg6-2g54-j896
- https://nvd.nist.gov/vuln/detail/CVE-2026-61644
- https://github.com/labring/FastGPT/commit/0c1840c7773c5be5d777f86228651479e02155db
- https://github.com/labring/FastGPT/pull/7173
