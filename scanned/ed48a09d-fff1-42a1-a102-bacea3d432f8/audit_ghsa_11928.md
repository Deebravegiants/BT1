# [M] Gokapi's File Request MaxSize Limit Bypassed via Multi-Chunk Upload

## Summary
Severity: Medium
Advisory: GHSA-45vh-rpc8-hxpp
CVE: CVE-2026-30961
CWE: CWE-20, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-45vh-rpc8-hxpp
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.4

## Details
### Summary

The chunked upload completion path for file requests does not validate the total file size against the per-request `MaxSize` limit. An attacker with a public file request link can split an oversized file into chunks each under `MaxSize` and upload them sequentially, bypassing the size restriction entirely. Files up to the server's global `MaxFileSizeMB` are accepted regardless of the file request's configured limit.

### Impact

Any guest with access to a shared file request link can upload files far larger than the administrator-configured size limit, up to the server's global `MaxFileSizeMB`. This allows unauthorized storage consumption, circumvention of administrative resource policies, and potential service disruption through storage exhaustion. No data exposure or privilege escalation occurs.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-45vh-rpc8-hxpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30961
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.4
- https://pkg.go.dev/vuln/GO-2026-4695
