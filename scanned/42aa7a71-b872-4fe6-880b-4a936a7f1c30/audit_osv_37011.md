# [M] Homarr: Unauthenticated Information Disclosure (Integration Metadata Leak)

## Summary
Severity: Medium
Advisory: CVE-2026-27796
Aliases: GHSA-m4vc-4prp-cvp7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-27796
Type: osv

## Details
Homarr is an open-source dashboard. Prior to version 1.54.0, the integration.all tRPC endpoint in Homarr is exposed as a publicProcedure, allowing unauthenticated users to retrieve a complete list of configured integrations. This metadata includes sensitive information such as internal service URLs, integration names, and service types. This issue has been patched in version 1.54.0.

## References
- https://github.com/homarr-labs/homarr/releases/tag/v1.54.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27796.json
- https://github.com/homarr-labs/homarr/security/advisories/GHSA-m4vc-4prp-cvp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27796
- https://github.com/homarr-labs/homarr/commit/91fc5a5c747121475a50f2713d571ceb89e95257
