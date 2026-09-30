# [?] fix race condition in tests

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-07-24
Source: https://github.com/multiversx/mx-chain-go/commit/21f27fd331b742cc233673ab201a3204b1e7f277
Type: security-commit

## Details
fix race condition in tests

## Patch
### consensus/chronology/chronology_test.go
```diff
@@ -1,6 +1,7 @@
 package chronology_test
 
 import (
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -433,10 +434,12 @@ func TestChronology_StartRounds(t *testing.T) {
 			},
 		}
 
-		updateRoundCalled := false
+		updateRoundCalled := &atomic.Bool{}
+		updateRoundCalled.Store(false)
+
 		arg.RoundHandler = &consensusMocks.RoundHandlerMock{
 			UpdateRoundCalled: func(t1, t2 time.Time) {
-				updateRoundCalled = true
+				updateRoundCalled.Store(true)
 			},
 		}
 
@@ -447,7 +450,7 @@ func TestChronology_StartRounds(t *testing.T) {
 
 		time.Sleep(5 * time.Millisecond)
 
-		require.True(t, updateRoundCalled)
+		require.True(t, updateRoundCalled.Load())
 	})
 }
 
```
