# [H] Bird-lg-go has a Fatal Out-of-Memory (OOM) Denial of Service via Unbounded JSON Decoding

## Summary
Severity: High
Advisory: GHSA-39qr-rc93-vhqm
CVE: CVE-2026-45047
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-39qr-rc93-vhqm
Type: github-advisory

## Affected
- Go: `github.com/xddxdd/bird-lg-go` — affected >=0 <0.0.0-20260507060110-0ff87024cb9e

## Details
### Summary
The `apiHandler` (and similarly `webHandlerTelegramBot`) processes user-provided JSON payloads by directly using `json.NewDecoder(r.Body).Decode(&request)` without restricting the maximum read size. An unauthenticated remote attacker can stream an extremely large, endless JSON payload (e.g., several Gigabytes of padding) over a single TCP connection. Because Go's JSON decoder attempts to allocate memory for the entire parsed structure, this rapidly exhausts the host's physical RAM or container limits, leading to an unrecoverable `fatal error: runtime: out of memory`. 

This causes the Linux OOM Killer to instantly terminate the entire `bird-lg-go` daemon, resulting in a severe Remote Denial of Service (RDoS).

### Details
In `api.go`:
```go
func apiHandler(w http.ResponseWriter, r *http.Request) {
    var request apiRequest
    // VULNERABILITY: No http.MaxBytesReader protection before JSON decode
    err := json.NewDecoder(r.Body).Decode(&request) 
    // ...

## References
- https://github.com/xddxdd/bird-lg-go/security/advisories/GHSA-39qr-rc93-vhqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45047
- https://github.com/xddxdd/bird-lg-go/commit/0ff87024cb9ed01fc5f5fdc6f4603fce4c123922
- https://github.com/xddxdd/bird-lg-go
- https://github.com/xddxdd/bird-lg-go/releases/tag/v1.4.5
