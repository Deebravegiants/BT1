# [M] Algernon: Race Condition in handle() shared LState

## Summary
Severity: Medium
Advisory: CVE-2026-43981
Aliases: GHSA-rr2f-4wrm-h6rg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43981
Type: osv

## Details
Algernon is a small self-contained pure-Go web server. Prior to 1.17.6, in engine/luahandler.go, the sync.RWMutex protecting LoadCommonFunctions is released before L.Push() and L.PCall() execute. Since gopher-lua's LState is explicitly not goroutine-safe, concurrent requests race on the shared state causing Lua VM corruption. The Go race detector confirms this immediately under modest concurrency (ab -n 1000 -c 100). This vulnerability is fixed in 1.17.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43981.json
- https://github.com/xyproto/algernon/security/advisories/GHSA-rr2f-4wrm-h6rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-43981
- https://github.com/xyproto/algernon/issues/172
