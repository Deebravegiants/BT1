# [M] OpenReplay: Cross-tenant session replay disclosure via missing session ownership check in first-mob endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-55881
Aliases: GHSA-w2x5-m7w5-479h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55881
Type: osv

## Details
OpenReplay is a self-hosted session replay suite. From 1.22.0 before 1.27.0, getFirstMob returned 15-second presigned S3 download URLs for a session's DOM-replay recording based solely on the session path parameter, while validateProjectAccess checked only that the project belonged to the requester's tenant and did not verify that the session belonged to that project, allowing any authenticated low-privilege user to read another tenant's first 15 seconds of session-replay recording data. This issue is fixed in version 1.27.0.

## References
- https://github.com/openreplay/openreplay/releases/tag/v1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55881.json
- https://github.com/openreplay/openreplay/security/advisories/GHSA-w2x5-m7w5-479h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55881
- https://github.com/openreplay/openreplay/commit/ddd09117f644a309c7b040cda0a11ff9433e9e49
- https://github.com/openreplay/openreplay/pull/4692
