# [C] Sandboxie's Integer Overflow in SbieIniServer::RC4Crypt allows sandbox escape and SYSTEM compromise

## Summary
Severity: Critical
Advisory: CVE-2025-64721
Aliases: GHSA-w476-j57g-96vp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-64721
Type: osv

## Details
Sandboxie is a sandbox-based isolation software for 32-bit and 64-bit Windows NT-based operating systems. In versions 1.16.6 and below, the SYSTEM-level service SbieSvc.exe exposes SbieIniServer::RC4Crypt to sandboxed processes. The handler adds a fixed header size to a caller-controlled value_len without overflow checking. A large value_len (e.g., 0xFFFFFFF0) wraps the allocation size, causing a heap overflow when attacker data is copied into the undersized buffer. This allows sandboxed processes to execute arbitrary code as SYSTEM, fully compromising the host. This issue is fixed in version 1.16.7.

## References
- https://github.com/sandboxie-plus/Sandboxie/releases/tag/v1.16.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64721.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-w476-j57g-96vp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64721
- https://github.com/sandboxie-plus/Sandboxie/commit/000492f8c411d24292f1b977a107994347bc7dfa
