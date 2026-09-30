# [?] fix(evmrpc): don't charge an innocent client's per-IP bucket on mid-read budget exhaustion (#3935)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-08-25
Source: https://github.com/sei-protocol/sei-chain/commit/198641f67b7ccf27c6a2daf2697e68a300c38dc0
Type: security-commit

## Details
fix(evmrpc): don't charge an innocent client's per-IP bucket on mid-read budget exhaustion (#3935)

## Describe your changes and provide context

`rateLimitMiddleware` and the outer `requestSizeLimiter` both watch the
same request body, but disagreed about who owns a mid-read failure. When
the global byte budget (`max_concurrent_request_bytes`) or the body-read
idle timeout was exhausted while `readBoundedBody` was reading, the
error surfaced to `rateLimitMiddleware` as a generic read failure. It
responded by charging the requesting client's own per-IP token bucket
(`chargeAdmissionRejection`) and recording a `read_error` rejection
metric — on top of the `budget_midread`/`slow_body` reason and metric
the outer `requestSizeLimiter` had already recorded for the same
request.

Two problems followed:
1. A well-behaved client could be pushed toward rate-limiting for a
purely server-side capacity event it didn't cause. Under load or an
actual DoS that exhausts the shared global budget, an innocent client
whose request happens to be mid-read at that moment gets its own bucket
debited for someone else's traffic.
2. `evmrpc_requests_rejected_total` double-counted the same rejected
request under two different reasons.

Flagged in review on #3836:
https://github.com/sei-protocol/sei-chain/pull/3836#discussion_r3735763876

### Fix

`rateLimitMiddleware` now recognizes `errBudgetExhausted` / a
read-idle-timeout error from `readBoundedBody` and returns without
charging admission or recording its own rejection reason, deferring
entirely to `requestSizeLimiter`, which already owns the correct reason
and the client-visible response.

## Testing performed to validate your change

- Added `TestComposedStack_BudgetMidreadDoesNotChargeInnocentIP`, which
holds the global budget open with one client's in-flight request and
verifies a second, distinct client's request that fails mid-read due to
budget exhaustion does not consume that client's own per-IP token (a
follow-up request from the same IP still succeeds under `burst=1`).
- Verified the new test fails without the fix and passes with it.
- `go test ./evmrpc/...` passes.
- `gofmt -s` / `goimports` clean on changed files.

---------

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### evmrpc/rate_limit_middleware.go
```diff
@@ -37,6 +37,15 @@ func (m *rateLimitMiddleware) ServeHTTP(w http.ResponseWriter, r *http.Request)
 			m.rejectAdmission(r.Context(), w, ip, rejectReasonOversize, http.StatusRequestEntityTooLarge, "request body too large")
 			return
 		}
+		if errors.Is(err, errBudgetExhausted) {
+			// Server-side capacity event; outer limiter already owns the response.
+			return
+		}
+		if errors.Is(err, errSlowBody) {
+			// Client-caused stall: still charge the per-IP bucket.
+			m.gate.ChargeAdmissionRejection(r.Context(), ip)
+			return
+		}
 		m.rejectAdmission(r.Context(), w, ip, rejectReasonReadError, http.StatusBadRequest, "bad request")
 		return
 	}
```

### evmrpc/rate_limit_middleware_test.go
```diff
@@ -504,3 +504,62 @@ func TestReadBoundedBody_RejectsOversize(t *testing.T) {
 		require.Equal(t, int64(len(body)), tracked.drained)
 	})
 }
+
+// TestComposedStack_BudgetMidreadDoesNotChargeInnocentIP guards against the
+// mid-read global-budget exhaustion of one client charging a different,
+// well-behaved client's per-IP bucket.
+func TestComposedStack_BudgetMidreadDoesNotChargeInnocentIP(t *testing.T) {
+	const maxBody = 1000
+	const budget = 1500 // room for exactly one max-size body at a time
+
+	release := make(chan struct{})
+	admitted := make(chan struct{}, 1)
+
+	reg := mustRateLimitRegistry(t, 0.001, 1) // burst=1: any charge exhausts the bucket
+	gate := newTestRateLimitGate(t, reg, maxBody)
+	inner := blockUntilRelease(release, func() { admitted <- struct{}{} })
+	stack := newRequestSizeLimiter(newRateLimitMiddleware(inner, gate), maxBody, budget, 0)
+
+	// A well-formed JSON-RPC body padded to exactly maxBody bytes: it must parse
+	// cleanly so the request reaches the byte-budget accounting inside
+	// readBoundedBody rather than getting rejected earlier as unparseable.
+	const prefix = `{"jsonrpc":"2.0","id":1,"method":"eth_call","params":["`
+	const suffix = `"]}`
+	fullSizeBody := prefix + strings.Repeat("x", maxBody-len(prefix)-len(suffix)) + suffix
+	require.Len(t, fullSizeBody, maxBody)
+
+	holderIP := "203.0.113.10:1"
+	victimIP := "203.0.113.20:1"
+
+	// The holder's request is admitted and reserves the whole budget, then blocks
+	// with its handler in flight so the reservation is not released yet.
+	firstDone := make(chan int, 1)
+	go func() {
+		rec := httptest.NewRecorder()
+		holderReq := newSizedRequest(fullSizeBody, maxBody)
+		holderReq.RemoteAddr = holderIP
+		stack.ServeHTTP(rec, holderReq)
+		firstDone <- rec.Code
+	}()
+	<-admitted
+
+	// The victim is a distinct, well-behaved client whose own request fails
+	// mid-read purely because the shared budget the holder reserved is gone.
+	rec := httptest.NewRecorder()
+	req := newSizedRequest(fullSizeBody, maxBody)
+	req.RemoteAddr = victimIP
+	stack.ServeHTTP(rec, req)
+	require.Equal(t, http.StatusTooManyRequests, rec.Code)
+	require.Contains(t, rec.Body.String(), "server busy")
+
+	close(release)
+	require.Equal(t, http.StatusOK, <-firstDone)
+
+	// The victim's own per-IP bucket must still be untouched: with burst=1, a
+	// request from that IP with room in the (now-released) budget still succeeds.
+	rec3 := httptest.NewRecorder()
+	req3 := newSizedRequest(`{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[]}`, -1)
+	req3.RemoteAddr = victimIP
+	stack.ServeHTTP(rec3, req3)
+	require.Equal(t, http.StatusOK, rec3.Code)
+}
```

### evmrpc/request_limiter.go
```diff
@@ -2,6 +2,7 @@ package evmrpc
 
 import (
 	"errors"
+	"fmt"
 	"io"
 	"net"
 	"net/http"
@@ -162,7 +163,7 @@ func (b *budgetBody) Read(p []byte) (int, error) {
 		}
 		if isReadIdleTimeout(err) {
 			b.fail(rejectReasonSlowBody, http.StatusRequestTimeout, "request timeout", err)
-			return n, err
+			return n, fmt.Errorf("%w: %w", errSlowBody, err)
 		}
 		b.release()
 	}
@@ -311,6 +312,7 @@ func (b *budgetBody) setOutcome(reason string, status int, message string) {
 }
 
 var errBudgetExhausted = errors.New("request byte budget exhausted")
+var errSlowBody = errors.New("request body read idle timeout")
 
 func isReadIdleTimeout(err error) bool {
 	if errors.Is(err, os.ErrDeadlineExceeded) {
```
