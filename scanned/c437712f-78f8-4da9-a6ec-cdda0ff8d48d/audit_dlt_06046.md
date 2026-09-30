# [?] blockchain/vm: fix data race on prestate tracer reason field

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-16
Source: https://github.com/kaiachain/kaia/commit/e75c40cd6dd19e3b6c7b7fa5367823aceb63ee59
Type: security-commit

## Details
blockchain/vm: fix data race on prestate tracer reason field

Stop() is called from the trace timeout goroutine while GetResult() reads
reason on the main goroutine, an unsynchronized access that trips the race
detector. Store it through atomic.Pointer, matching how interrupt is handled.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### blockchain/vm/prestate_tracer.go
```diff
@@ -81,7 +81,7 @@ type PrestateTracer struct {
 	synthFee    *big.Int
 
 	interrupt atomic.Bool
-	reason    error
+	reason    atomic.Pointer[error]
 }
 
 // NewPrestateTracer constructs a PrestateTracer. cfg may be nil.
@@ -233,11 +233,14 @@ func (t *PrestateTracer) GetResult() (json.RawMessage, error) {
 	if err != nil {
 		return nil, err
 	}
-	return res, t.reason
+	if reason := t.reason.Load(); reason != nil {
+		return res, *reason
+	}
+	return res, nil
 }
 
 func (t *PrestateTracer) Stop(err error) {
-	t.reason = err
+	t.reason.Store(&err)
 	t.interrupt.Store(true)
 }
 
```
