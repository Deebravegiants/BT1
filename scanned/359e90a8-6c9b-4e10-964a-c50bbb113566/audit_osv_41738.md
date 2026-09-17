# [M] Chatwoot < 4.16.0 Unauthenticated ActiveStorage Direct Upload Arbitrary Blob Creation

## Summary
Severity: Medium
Advisory: CVE-2026-63765
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-63765
Type: osv

## Details
Chatwoot before 4.16.0 contains an authentication bypass vulnerability in the direct uploads controller that allows unauthenticated attackers to create arbitrary ActiveStorage blobs in any tenant account. Attackers can exploit missing authentication checks to resolve any account and conversation, then obtain signed PUT URLs to write arbitrary data to the application's storage backend.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63765.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63765
- https://www.vulncheck.com/advisories/chatwoot-unauthenticated-activestorage-direct-upload-arbitrary-blob-creation
- https://github.com/chatwoot/chatwoot/issues/15072
- https://github.com/chatwoot/chatwoot/commit/8dd0d08322edafaec24624b72ed2f6045921cb7b
- https://github.com/chatwoot/chatwoot/pull/15039
- https://github.com/chatwoot/chatwoot/releases/tag/v4.16.0
- https://github.com/chatwoot/chatwoot
