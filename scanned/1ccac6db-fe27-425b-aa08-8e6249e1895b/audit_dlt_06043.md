# [?] vm: fix data race on CallTracer interruptReason

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-25
Source: https://github.com/kaiachain/kaia/commit/0a29eb48a894cd5b3dcb255d21c408e81216b9c9
Type: security-commit

## Details
vm: fix data race on CallTracer interruptReason

Stop() (timeout goroutine) and GetResult() (main goroutine) accessed
interruptReason concurrently with no happens-before edge. Write the reason
before the release Store in Stop(), and read it in GetResult() only after
an acquire interrupt.Load().

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

## Patch
### blockchain/vm/call_tracer.go
```diff
@@ -224,13 +224,16 @@ func (t *CallTracer) GetResult() (CallFrame, error) {
 		return CallFrame{}, errors.New("incorrect number of top-level calls")
 	}
 
-	// Return with interrupt reason if any
-	return t.callstack[0], t.interruptReason
+	// Read interruptReason only after observing the flag, so Stop()'s write happens-before this read.
+	if t.interrupt.Load() {
+		return t.callstack[0], t.interruptReason
+	}
+	return t.callstack[0], nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
 // For CallTracer, it stops at CaptureEnter, which is the most repetitive operation.
 func (t *CallTracer) Stop(err error) {
-	t.interrupt.Store(true)
 	t.interruptReason = err
+	t.interrupt.Store(true)
 }
```
