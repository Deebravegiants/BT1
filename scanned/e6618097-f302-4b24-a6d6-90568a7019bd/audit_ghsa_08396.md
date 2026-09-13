# [M] Algernon: Auto-refresh SSE event server binds to all interfaces with Access-Control-Allow-Origin: * and no authentication

## Summary
Severity: Medium
Advisory: GHSA-9v4j-7g44-qcqw
CWE: CWE-1188, CWE-200, CWE-306, CWE-942
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-9v4j-7g44-qcqw
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.7

## Details
### Summary

When auto-refresh is enabled, Algernon spins up an SSE handler that streams a `data:` line for every filesystem event under the watched directory. The handler performs **no authentication** of any kind — no shared token, no cookie check against the `permissions2` userstate, no IP allow-list, no path-prefix permission. Any client that can complete a TCP connection to the listener address receives the stream.

This advisory covers the authentication gap in isolation. The cross-origin browser-reach (advisory #2b) and the network-reach (advisory #2c) amplify the impact, but each is independently fixable; this finding addresses the case where a same-origin or LAN-local client connects directly to the SSE port and reads the stream without proving anything about its identity.

### Details

#### Root cause — the SSE handler does not consult `permissions2` or any other auth

```go
// vendor/github.com/xyproto/recwatch/eventserver.go:100-144  (1.17.6)
func GenFileChangeEvents(events TimeEventMap, mut *sync.Mutex, maxAge time.Duration, allowed string) http.HandlerFunc {
    return func(w http.ResponseWriter, _ *http.Request) {
        w.Header().Set("Content-Type", "text/event-stream;charset=utf-8")
        w.Header().Set("Cache-Control", "no-cache")
        w.Header().Set("Connection", "keep-alive")
        w.Header().Set("Access-Control-Allow-Origin", allowed)
        // ... loop emits one SSE record per filename touched ...
    }
}
```

Note the handler signature: `func(w http.ResponseWriter, _ *http.Request)`. The request is discarded — no `Cookie`, `Authorization`, query-string, or remote-IP check is performed before the stream begins.

In 1.17.6 the listener was placed on its own `http.ServeMux` ([recwatch/eventserver.go:200-215](../vendor/github.com/xyproto/recwatch/eventserver.go)), wholly outside the `perm.Rejected` middleware chain that gates Algernon's main HTTP listener. Even an operator who had configured admin/user path prefixes via `perm.AddAdminPath`, set a `cookieSecret`, and forced authentication on every URL of the main server had no way to gate this listener — it was unreachable from the `mux` argument the perm middleware uses.

#### Why authentication matters for this listener

The stream contents are not public data. They reveal:

- Which files the developer is actively editing, with sub-second timing precision.
- The existence of files inside the watched root (including files the operator may have meant to keep private — `.env.local`, `secrets.lua`, in-progress draft files).
- By inference, the directory layout of the project.

A client that can connect to the listener obtains a low-rate continuous information disclosure for the lifetime of the connection. The handler is an infinite `for {}` loop — there is no natural session boundary or expiry.

#### Source-level evidence

```text
$ rg -n 'GenFileChangeEvents|EventServer\(' vendor/github.com/xyproto/recwatch/
vendor/github.com/xyproto/recwatch/eventserver.go:101:func GenFileChangeEvents(events TimeEventMap, mut *sync.Mutex, maxAge time.Duration, allowed string) http.HandlerFunc {
vendor/github.com/xyproto/recwatch/eventserver.go:177:func EventServer(path, allowed, eventAddr, eventPath string, refreshDuration time.Duration) {

$ rg -n 'Cookie|Authorization|Token|state\.User' vendor/github.com/xyproto/recwatch/eventserver.go
# zero matches — no authentication primitive is referenced anywhere in the file
```

### PoC (against 1.17.6)

```bash
# 1. Operator runs algernon with auto-refresh on a project directory:
algernon -a /path/to/project   # spins up :5553 on Linux/macOS, localhost:5553 on Windows

# 2. Any client that can reach the listener connects without credentials:
curl -sN http://<server>:5553/sse
# => id: 0
#    data: /path/to/project/secret-notes.md
#
#    id: 1
#    data: /path/to/project/.env.local
```

No `Cookie`, no `Authorization`, no `X-Token`, no preflight, no challenge. The connection succeeds and the stream is delivered for as long as the client keeps the socket open.

### Impact

- **Confidentiality:** medium. Continuous information disclosure of filenames and edit timing to anyone who can connect.
- **Integrity:** none.
- **Availability:** low. Each connection consumes a goroutine indefinitely; many simultaneous connections can exhaust descriptors.

### Suggestions to fix

**Primary fix — require a shared secret on the SSE endpoint.** The auto-refresh feature already injects a script into served HTML ([engine/sse.go:118-165](../engine/sse.go)); that script knows the SSE URL. Add a per-startup token, embed it in the injected JS, and require it on the SSE request:

```go
// engine/sse.go -- in InsertAutoRefresh
tmplData.SessionToken = ac.sseToken    // generated once at startup, e.g. crypto/rand 32 bytes

// JS:
//   var source = new EventSource('...?token={{.SessionToken}}');

// recwatch handler:
//   if subtle.ConstantTimeCompare([]byte(r.URL.Query().Get("token")),
//                                 []byte(serverToken)) != 1 {
//       http.Error(w, "forbidden", http.StatusForbidden); return
//   }
```

Cookie-bearing requests work too if `recwatch.EventServer` is moved behind `perm.Rejected` (see "Defence in depth"). The token approach is the smaller change.

**Defence in depth — mount the SSE handler on the main mux.** Moving `recwatch.EventServerHandler` onto the main `http.ServeMux` automatically places the SSE handler behind whatever middleware the operator has configured — `perm.Rejected`, `tollbooth`, custom auth wrappers. This closes the same-origin half of the gap without a per-token implementation. Any dedicated-port path bypasses `perm.Rejected` because it uses its own `http.ServeMux`, and that path needs the token fix from "Primary fix" above.

### Live verification

```
$ ./algernon.exe --nodb --httponly --server -a --addr 127.0.0.1:18781 --quiet poc2/site
$ ( curl -sN --max-time 4 http://127.0.0.1:5553/sse > stream.txt &
    sleep 1
    echo "edit-1" >> poc2/site/secret-notes.md
    echo "edit-2" >> poc2/site/.env.local
    wait )
$ cat stream.txt
id: 0
data: C:\Users\xbox\Desktop\VulnTesting\algernon-main\poc-test\poc2\site\secret-notes.md

id: 1
data: C:\Users\xbox\Desktop\VulnTesting\algernon-main\poc-test\poc2\site\.env.local
```

No `Cookie`, no `Authorization` header. Stream delivered.

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-9v4j-7g44-qcqw
- https://github.com/xyproto/algernon
