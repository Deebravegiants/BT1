# [?] eth/tracers: fix data race on interruption reason across tracers (#34827)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-05-11
Source: https://github.com/ethereum/go-ethereum/commit/22919cec1b257b3f2d3a2c348f432c08efae7114
Type: security-commit

## Details
eth/tracers: fix data race on interruption reason across tracers (#34827)

Every tracer that implements Stop/GetResult held a `reason error` field
that is written by Stop (called from the trace-timeout watchdog
goroutine in api.go) and read by GetResult (called by the RPC handler
main goroutine). These accesses were unsynchronized.

## Patch
### eth/tracers/logger/logger.go
```diff
@@ -229,9 +229,9 @@ type StructLogger struct {
 	logs       []json.RawMessage // buffer of json-encoded logs
 	resultSize int
 
-	interrupt atomic.Bool // Atomic flag to signal execution interruption
-	reason    error       // Textual reason for the interruption
-	skip      bool        // skip processing hooks.
+	interrupt atomic.Bool           // Atomic flag to signal execution interruption
+	reason    atomic.Pointer[error] // Reason for the interruption, populated by Stop
+	skip      bool                  // skip processing hooks.
 }
 
 // NewStreamingStructLogger returns a new streaming logger.
@@ -357,8 +357,8 @@ func (l *StructLogger) OnExit(depth int, output []byte, gasUsed uint64, err erro
 
 func (l *StructLogger) GetResult() (json.RawMessage, error) {
 	// Tracing aborted
-	if l.reason != nil {
-		return nil, l.reason
+	if p := l.reason.Load(); p != nil {
+		return nil, *p
 	}
 	failed := l.err != nil
 	returnData := common.CopyBytes(l.output)
@@ -376,7 +376,7 @@ func (l *StructLogger) GetResult() (json.RawMessage, error) {
 
 // Stop terminates execution of the tracer at the first opportune moment.
 func (l *StructLogger) Stop(err error) {
-	l.reason = err
+	l.reason.Store(&err)
 	l.interrupt.Store(true)
 }
 
```

### eth/tracers/native/4byte.go
```diff
@@ -49,9 +49,9 @@ func init() {
 //	  0xc281d19e-0: 1
 //	}
 type fourByteTracer struct {
-	ids               map[string]int // ids aggregates the 4byte ids found
-	interrupt         atomic.Bool    // Atomic flag to signal execution interruption
-	reason            error          // Textual reason for the interruption
+	ids               map[string]int        // ids aggregates the 4byte ids found
+	interrupt         atomic.Bool           // Atomic flag to signal execution interruption
+	reason            atomic.Pointer[error] // Reason for the interruption, populated by Stop
 	chainConfig       *params.ChainConfig
 	activePrecompiles []common.Address // Updated on tx start based on given rules
 }
@@ -124,12 +124,15 @@ func (t *fourByteTracer) GetResult() (json.RawMessage, error) {
 	if err != nil {
 		return nil, err
 	}
-	return res, t.reason
+	if p := t.reason.Load(); p != nil {
+		return res, *p
+	}
+	return res, nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
 func (t *fourByteTracer) Stop(err error) {
-	t.reason = err
+	t.reason.Store(&err)
 	t.interrupt.Store(true)
 }
 
```

### eth/tracers/native/call.go
```diff
@@ -116,8 +116,8 @@ type callTracer struct {
 	config    callTracerConfig
 	gasLimit  uint64
 	depth     int
-	interrupt atomic.Bool // Atomic flag to signal execution interruption
-	reason    error       // Textual reason for the interruption
+	interrupt atomic.Bool           // Atomic flag to signal execution interruption
+	reason    atomic.Pointer[error] // Reason for the interruption, populated by Stop
 }
 
 type callTracerConfig struct {
@@ -268,12 +268,15 @@ func (t *callTracer) GetResult() (json.RawMessage, error) {
 	if err != nil {
 		return nil, err
 	}
-	return res, t.reason
+	if p := t.reason.Load(); p != nil {
+		return res, *p
+	}
+	return res, nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
 func (t *callTracer) Stop(err error) {
-	t.reason = err
+	t.reason.Store(&err)
 	t.interrupt.Store(true)
 }
 
```

### eth/tracers/native/call_flat.go
```diff
@@ -233,7 +233,10 @@ func (t *flatCallTracer) GetResult() (json.RawMessage, error) {
 	if err != nil {
 		return nil, err
 	}
-	return res, t.tracer.reason
+	if p := t.tracer.reason.Load(); p != nil {
+		return res, *p
+	}
+	return res, nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
```

### eth/tracers/native/erc7562.go
```diff
@@ -135,8 +135,8 @@ type opcodeWithPartialStack struct {
 type erc7562Tracer struct {
 	config    erc7562TracerConfig
 	gasLimit  uint64
-	interrupt atomic.Bool // Atomic flag to signal execution interruption
-	reason    error       // Textual reason for the interruption
+	interrupt atomic.Bool           // Atomic flag to signal execution interruption
+	reason    atomic.Pointer[error] // Reason for the interruption, populated by Stop
 	env       *tracing.VMContext
 
 	ignoredOpcodes       map[vm.OpCode]struct{}
@@ -317,7 +317,10 @@ func (t *erc7562Tracer) OnLog(log1 *types.Log) {
 // error arising from the encoding or forceful termination (via `Stop`).
 func (t *erc7562Tracer) GetResult() (json.RawMessage, error) {
 	if t.interrupt.Load() {
-		return nil, t.reason
+		if p := t.reason.Load(); p != nil {
+			return nil, *p
+		}
+		return nil, nil
 	}
 	if len(t.callstackWithOpcodes) != 1 {
 		return nil, errors.New("incorrect number of top-level calls")
@@ -337,12 +340,15 @@ func (t *erc7562Tracer) GetResult() (json.RawMessage, error) {
 		return nil, err
 	}
 
-	return enc, t.reason
+	if p := t.reason.Load(); p != nil {
+		return enc, *p
+	}
+	return enc, nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
 func (t *erc7562Tracer) Stop(err error) {
-	t.reason = err
+	t.reason.Store(&err)
 	t.interrupt.Store(true)
 }
 
```

### eth/tracers/native/prestate.go
```diff
@@ -71,8 +71,8 @@ type prestateTracer struct {
 	to          common.Address
 	config      PrestateTracerConfig
 	chainConfig *params.ChainConfig
-	interrupt   atomic.Bool // Atomic flag to signal execution interruption
-	reason      error       // Textual reason for the interruption
+	interrupt   atomic.Bool           // Atomic flag to signal execution interruption
+	reason      atomic.Pointer[error] // Reason for the interruption, populated by Stop
 	created     map[common.Address]bool
 	deleted     map[common.Address]bool
 }
@@ -240,12 +240,15 @@ func (t *prestateTracer) GetResult() (json.RawMessage, error) {
 	if err != nil {
 		return nil, err
 	}
-	return json.RawMessage(res), t.reason
+	if p := t.reason.Load(); p != nil {
+		return json.RawMessage(res), *p
+	}
+	return json.RawMessage(res), nil
 }
 
 // Stop terminates execution of the tracer at the first opportune moment.
 func (t *prestateTracer) Stop(err error) {
-	t.reason = err
+	t.reason.Store(&err)
 	t.interrupt.Store(true)
 }
 
```

### eth/tracers/native/tracer_test.go
```diff
@@ -0,0 +1,80 @@
+// Copyright 2026 The go-ethereum Authors
+// This file is part of the go-ethereum library.
+//
+// The go-ethereum library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The go-ethereum library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+
+package native_test
+
+import (
+	"errors"
+	"math/big"
+	"sync"
+	"testing"
+
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core/vm"
+	"github.com/ethereum/go-ethereum/eth/tracers"
+	"github.com/ethereum/go-ethereum/params"
+	"github.com/stretchr/testify/require"
+)
+
+// TestTracerStopRace exercises the concurrent Stop / GetResult path that the
+// trace RPC handler uses: a timeout watchdog goroutine calls Stop while the
+// main goroutine is still running the trace and will eventually call
+// GetResult. Under -race, writes to the interruption reason field must not
+// race with reads, for every tracer that implements it.
+//
+// callTracer, flatCallTracer and erc7562Tracer's GetResult short-circuits on
+// an empty callstack ("incorrect number of top-level calls") before loading
+// the reason. For those tracers the test pushes a single top-level call frame
+// via OnEnter so GetResult reaches the reason.Load() path where the race can
+// be observed under -race.
+func TestTracerStopRace(t *testing.T) {
+	type setup struct {
+		name       string
+		needsFrame bool // whether GetResult requires a top-level call frame
+	}
+	cases := []setup{
+		{"callTracer", true},
+		{"flatCallTracer", true},
+		{"4byteTracer", false},
+		{"prestateTracer", false},
+		{"erc7562Tracer", true},
+	}
+	for _, s := range cases {
+		t.Run(s.name, func(t *testing.T) {
+			tr, err := tracers.DefaultDirectory.New(s.name, &tracers.Context{}, nil, params.MainnetChainConfig)
+			require.NoError(t, err)
+
+			if s.needsFrame && tr.OnEnter != nil {
+				// Push a single top-level call frame so GetResult doesn't
+				// short-circuit before reading the interruption reason.
+				tr.OnEnter(0, byte(vm.CALL), common.Address{}, common.Address{}, nil, 0, big.NewInt(0))
+			}
+
+			stopErr := errors.New("execution timeout")
+			var wg sync.WaitGroup
+			wg.Add(2)
+			go func() {
+				defer wg.Done()
+				tr.Stop(stopErr)
+			}()
+			go func() {
+				defer wg.Done()
+				_, _ = tr.GetResult()
+			}()
+			wg.Wait()
+		})
+	}
+}
```
