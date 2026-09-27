# [H] DragonflyDB `CMS.INITBYDIM` integer overflow leads to a remote, attacker-controlled heap out-of-bounds write

## Summary
Severity: High
Advisory: CVE-2026-62357
Aliases: GHSA-cmmv-h748-v93x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-62357
Type: osv

## Details
Dragonfly is an in-memory data store built for modern application workloads. Prior to 1.40.0, CMS.INITBYDIM and CMS.INITBYPROB accept dimensions whose width times depth times sizeof(int64_t) overflows in src/core/cms.cc, allocating an undersized counter buffer while CMS.INCRBY and CMS.QUERY use the unbounded dimensions, which allows an unauthenticated remote client to corrupt or disclose adjacent heap memory and crash the server. This issue is fixed in version 1.40.0.

## References
- https://github.com/dragonflydb/dragonfly/releases/tag/v1.40.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62357.json
- https://github.com/dragonflydb/dragonfly/security/advisories/GHSA-cmmv-h748-v93x
- https://nvd.nist.gov/vuln/detail/CVE-2026-62357
- https://github.com/dragonflydb/dragonfly/commit/c004623249fe2151dc5d64e21364fb9fb07c90d3
- https://github.com/dragonflydb/dragonfly/pull/7647
