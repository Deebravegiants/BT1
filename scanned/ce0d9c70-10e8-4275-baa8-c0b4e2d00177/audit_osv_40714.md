# [M] FastGPT: reTrainingCollection allows server-owned datasetId override causing cross-tenant authorization confusion

## Summary
Severity: Medium
Advisory: CVE-2026-54601
Aliases: GHSA-qxcq-48gr-93pj
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-54601
Type: osv

## Details
FastGPT is an open source AI knowledge base platform. From 4.14.17 to before 4.15.0-beta4, FastGPT allows an authenticated tenant user to call POST /api/core/dataset/collection/create/reTrainingCollection in a way that persists a server-owned datasetId value from another tenant. This creates mixed dataset objects and downstream dataset, collection, and training endpoints then make authorization decisions from inconsistent ownership anchors, allowing cross-tenant read, update, and delete access when mixed object ids are known. This issue is fixed in version 4.15.0-beta4.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54601.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-qxcq-48gr-93pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54601
- https://github.com/labring/FastGPT/commit/54a53e7d4399f1dfa2913394442c3cf6de672fb3
- https://github.com/labring/FastGPT/pull/7071
