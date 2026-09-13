# [M] goshs has Cross-Origin Arbitrary File Write via Missing CSRF on PUT and Wildcard CORS

## Summary
Severity: Medium
Advisory: GHSA-rhf7-wvw3-vjvm
CVE: CVE-2026-42091
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-rhf7-wvw3-vjvm
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.0.2
- Go: `github.com/patrickhener/goshs` — affected >=0

## Details
### Summary
The PUT upload handler (`httpserver/updown.go`) lacks the CSRF token validation that was added to the POST upload handler during the GHSA-jrq5-hg6x-j6g3 fix. Combined with the unconditional `Access-Control-Allow-Origin: *` on the OPTIONS preflight handler (`httpserver/server.go`), any website can write arbitrary files to a goshs instance through the victim's browser — bypassing network isolation (e.g. localhost, internal network).

### Details
**Root Cause 1 — Missing CSRF on PUT** (`httpserver/updown.go:19`)

When GHSA-jrq5-hg6x-j6g3 was fixed (commit `e3c3d37`), `checkCSRF()` was added to the POST `upload()` function (line 78) but not to the PUT `put()` function directly above it in the same file. This means PUT requests are accepted without any CSRF token.

```go
// POST — protected 
func (fs *FileServer) upload(w http.ResponseWriter, req *http.Request) {
    if !fs.checkCSRF(w, req) { return }
    // ...
}

// PUT — unprotected 
func (fs *FileServer) put(w http.ResponseWriter, req *http.Request) {
    // No checkCSRF call
    // ...
}
```

**Root Cause 2 — Wildcard CORS** (`httpserver/server.go:126`)

The OPTIONS handler unconditionally returns permissive CORS headers:

```go
w.Header().Set("Access-Control-Allow-Origin", "*")
w.Header().Set("Access-Control-Allow-Methods", "POST, PUT, OPTIONS")
w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
```

This allows any website's JavaScript to pass the browser's CORS preflight check and send PUT requests to the goshs server.

### PoC
[poc.zip](https://github.com/user-attachments/files/26828829/poc.zip)

Please extract the uploaded compressed file before proceeding

1. bash poc.sh
<img width="543" height="376" alt="스크린샷 2026-04-17 오후 11 08 13" src="https://github.com/user-attachments/assets/a695cbc8-133e-4e80-a2f5-9fe9fd36b569" />




### Impact
- Arbitrary file write to the goshs webroot from any website the victim visits
- File overwrite — existing files can be silently replaced

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-rhf7-wvw3-vjvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42091
- https://github.com/patrickhener/goshs/commit/0e715b94e10c3d1aa552276000f15f104dee2f32
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.2
