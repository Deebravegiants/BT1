# [?] eth/tracers/native: prevent panic for LOG edge-cases (#26848)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-03-28
Source: https://github.com/ethereum/go-ethereum/commit/fd94b4fcfa244179c0500b70fb2944cb686b9ca4
Type: security-commit

## Details
eth/tracers/native: prevent panic for LOG edge-cases (#26848)

This PR fixes OOM panic in the callTracer as well as panicing on
opcode validation errors (e.g. stack underflow) in callTracer and
prestateTracer.

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### eth/tracers/internal/tracetest/calltrace_test.go
```diff
@@ -31,7 +31,6 @@ import (
 	"github.com/ethereum/go-ethereum/core/rawdb"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/core/vm"
-	"github.com/ethereum/go-ethereum/crypto"
 	"github.com/ethereum/go-ethereum/eth/tracers"
 	"github.com/ethereum/go-ethereum/params"
 	"github.com/ethereum/go-ethereum/rlp"
@@ -260,75 +259,121 @@ func benchTracer(tracerName string, test *callTracerTest, b *testing.B) {
 	}
 }
 
-// TestZeroValueToNotExitCall tests the calltracer(s) on the following:
-// Tx to A, A calls B with zero value. B does not already exist.
-// Expected: that enter/exit is invoked and the inner call is shown in the result
-func TestZeroValueToNotExitCall(t *testing.T) {
-	var to = common.HexToAddress("0x00000000000000000000000000000000deadbeef")
-	privkey, err := crypto.HexToECDSA("0000000000000000deadbeef00000000000000000000000000000000deadbeef")
-	if err != nil {
-		t.Fatalf("err %v", err)
-	}
-	signer := types.NewEIP155Signer(big.NewInt(1))
-	tx, err := types.SignNewTx(privkey, signer, &types.LegacyTx{
-		GasPrice: big.NewInt(0),
-		Gas:      50000,
-		To:       &to,
-	})
-	if err != nil {
-		t.Fatalf("err %v", err)
-	}
-	origin, _ := signer.Sender(tx)
-	txContext := vm.TxContext{
-		Origin:   origin,
-		GasPrice: big.NewInt(1),
-	}
-	context := vm.BlockContext{
-		CanTransfer: core.CanTransfer,
-		Transfer:    core.Transfer,
-		Coinbase:    common.Address{},
-		BlockNumber: new(big.Int).SetUint64(8000000),
-		Time:        5,
-		Difficulty:  big.NewInt(0x30000),
-		GasLimit:    uint64(6000000),
-	}
-	var code = []byte{
-		byte(vm.PUSH1), 0x0, byte(vm.DUP1), byte(vm.DUP1), byte(vm.DUP1), // in and outs zero
-		byte(vm.DUP1), byte(vm.PUSH1), 0xff, byte(vm.GAS), // value=0,address=0xff, gas=GAS
-		byte(vm.CALL),
+func TestInternals(t *testing.T) {
+	var (
+		to        = common.HexToAddress("0x00000000000000000000000000000000deadbeef")
+		origin    = common.HexToAddress("0x00000000000000000000000000000000feed")
+		txContext = vm.TxContext{
+			Origin:   origin,
+			GasPrice: big.NewInt(1),
+		}
+		context = vm.BlockContext{
+			CanTransfer: core.CanTransfer,
+			Transfer:    core.Transfer,
+			Coinbase:    common.Address{},
+			BlockNumber: new(big.Int).SetUint64(8000000),
+			Time:        5,
+			Difficulty:  big.NewInt(0x30000),
+			GasLimit:    uint64(6000000),
+		}
+	)
+	mkTracer := func(name string, cfg json.RawMessage) tracers.Tracer {
+		tr, err := tracers.DefaultDirectory.New(name, nil, cfg)
+		if err != nil {
+			t.Fatalf("failed to create call tracer: %v", err)
+		}
+		return tr
 	}
-	var alloc = core.GenesisAlloc{
-		to: core.GenesisAccount{
-			Nonce: 1,
-			Code:  code,
+
+	for _, tc := range []struct {
+		name   string
+		code   []byte
+		tracer tracers.Tracer
+		want   string
+	}{
+		{
+			// TestZeroValueToNotExitCall tests the calltracer(s) on the following:
+			// Tx to A, A calls B with zero value. B does not already exist.
+			// Expected: that enter/exit is invoked and the inner call is shown in the result
+			name: "ZeroValueToNotExitCall",
+			code: []byte{
+				byte(vm.PUSH1), 0x0, byte(vm.DUP1), byte(vm.DUP1), byte(vm.DUP1), // in and outs zero
+				byte(vm.DUP1), byte(vm.PUSH1), 0xff, byte(vm.GAS), // value=0,address=0xff, gas=GAS
+				byte(vm.CALL),
+			},
+			tracer: mkTracer("callTracer", nil),
+			want:   `{"from":"0x000000000000000000000000000000000000feed","gas":"0x7148","gasUsed":"0x54d8","to":"0x00000000000000000000000000000000deadbeef","input":"0x","calls":[{"from":"0x00000000000000000000000000000000deadbeef","gas":"0x6cbf","gasUsed":"0x0","to":"0x00000000000000000000000000000000000000ff","input":"0x","value":"0x0","type":"CALL"}],"value":"0x0","type":"CALL"}`,
 		},
-		origin: core.GenesisAccount{
-			Nonce:   0,
-			Balance: big.NewInt(500000000000000),
+		{
+			name:   "Stack depletion in LOG0",
+			code:   []byte{byte(vm.LOG3)},
+			tracer: mkTracer("callTracer", json.RawMessage(`{ "withLog": true }`)),
+			want:   `{"from":"0x000000000000000000000000000000000000feed","gas":"0x7148","gasUsed":"0xc350","to":"0x00000000000000000000000000000000deadbeef","input":"0x","error":"stack underflow (0 \u003c=\u003e 5)","value":"0x0","type":"CALL"}`,
 		},
-	}
-	_, statedb := tests.MakePreState(rawdb.NewMemoryDatabase(), alloc, false)
-	// Create the tracer, the EVM environment and run it
-	tracer, err := tracers.DefaultDirectory.New("callTracer", nil, nil)
-	if err != nil {
-		t.Fatalf("failed to create call tracer: %v", err)
-	}
-	evm := vm.NewEVM(context, txContext, statedb, params.MainnetChainConfig, vm.Config{Debug: true, Tracer: tracer})
-	msg, err := core.TransactionToMessage(tx, signer, nil)
-	if err != nil {
-		t.Fatalf("failed to prepare transaction for tracing: %v", err)
-	}
-	st := core.NewStateTransition(evm, msg, new(core.GasPool).AddGas(tx.Gas()))
-	if _, err = st.TransitionDb(); err != nil {
-		t.Fatalf("failed to execute transaction: %v", err)
-	}
-	// Retrieve the trace result and compare against the etalon
-	res, err := tracer.GetResult()
-	if err != nil {
-		t.Fatalf("failed to retrieve trace result: %v", err)
-	}
-	wantStr := `{"from":"0x682a80a6f560eec50d54e63cbeda1c324c5f8d1b","gas":"0x7148","gasUsed":"0x54d8","to":"0x00000000000000000000000000000000deadbeef","input":"0x","calls":[{"from":"0x00000000000000000000000000000000deadbeef","gas":"0x6cbf","gasUsed":"0x0","to":"0x00000000000000000000000000000000000000ff","input":"0x","value":"0x0","type":"CALL"}],"value":"0x0","type":"CALL"}`
-	if string(res) != wantStr {
-		t.Fatalf("trace mismatch\n have: %v\n want: %v\n", string(res), wantStr)
+		{
+			name: "Mem expansion in LOG0",
+			code: []byte{
+				byte(vm.PUSH1), 0x1,
+				byte(vm.PUSH1), 0x0,
+				byte(vm.MSTORE),
+				byte(vm.PUSH1), 0xff,
+				byte(vm.PUSH1), 0x0,
+				byte(vm.LOG0),
+			},
+			tracer: mkTracer("callTracer", json.RawMessage(`{ "withLog": true }`)),
+			want:   `{"from":"0x000000000000000000000000000000000000feed","gas":"0x7148","gasUsed":"0x5b9e","to":"0x00000000000000000000000000000000deadbeef","input":"0x","logs":[{"address":"0x00000000000000000000000000000000deadbeef","topics":[],"data":"0x000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"}],"value":"0x0","type":"CALL"}`,
+		},
+		{
+			// Leads to OOM on the prestate tracer
+			name: "Prestate-tracer - mem expansion in CREATE2",
+			code: []byte{
+				byte(vm.PUSH1), 0x1,
+				byte(vm.PUSH1), 0x0,
+				byte(vm.MSTORE),
+				byte(vm.PUSH1), 0x1,
+				byte(vm.PUSH5), 0xff, 0xff, 0xff, 0xff, 0xff,
+				byte(vm.PUSH1), 0x1,
+				byte(vm.PUSH1), 0x0,
+				byte(vm.CREATE2),
+				byte(vm.PUSH1), 0xff,
+				byte(vm.PUSH1), 0x0,
+				byte(vm.LOG0),
+			},
+			tracer: mkTracer("prestateTracer", json.RawMessage(`{ "withLog": true }`)),
+			want:   `{"0x0000000000000000000000000000000000000000":{"balance":"0x0"},"0x000000000000000000000000000000000000feed":{"balance":"0x1c6bf52640350"},"0x00000000000000000000000000000000deadbeef":{"balance":"0x0","code":"0x6001600052600164ffffffffff60016000f560ff6000a0"}}`,
+		},
+	} {
+		_, statedb := tests.MakePreState(rawdb.NewMemoryDatabase(),
+			core.GenesisAlloc{
+				to: core.GenesisAccount{
+					Code: tc.code,
+				},
+				origin: core.GenesisAccount{
+					Balance: big.NewInt(500000000000000),
+				},
+			}, false)
+		evm := vm.NewEVM(context, txContext, statedb, params.MainnetChainConfig, vm.Config{Debug: true, Tracer: tc.tracer})
+		msg := &core.Message{
+			To:                &to,
+			From:              origin,
+			Value:             big.NewInt(0),
+			GasLimit:          50000,
+			GasPrice:          big.NewInt(0),
+			GasFeeCap:         big.NewInt(0),
+			GasTipCap:         big.NewInt(0),
+			SkipAccountChecks: false,
+		}
+		st := core.NewStateTransition(evm, msg, new(core.GasPool).AddGas(msg.GasLimit))
+		if _, err := st.TransitionDb(); err != nil {
+			t.Fatalf("test %v: failed to execute transaction: %v", tc.name, err)
+		}
+		// Retrieve the trace result and compare against the expected
+		res, err := tc.tracer.GetResult()
+		if err != nil {
+			t.Fatalf("test %v: failed to retrieve trace result: %v", tc.name, err)
+		}
+		if string(res) != tc.want {
+			t.Fatalf("test %v: trace mismatch\n have: %v\n want: %v\n", tc.name, string(res), tc.want)
+		}
 	}
 }
```

### eth/tracers/js/goja.go
```diff
@@ -32,10 +32,6 @@ import (
 	jsassets "github.com/ethereum/go-ethereum/eth/tracers/js/internal/tracers"
 )
 
-const (
-	memoryPadLimit = 1024 * 1024
-)
-
 var assetTracers = make(map[string]string)
 
 // init retrieves the JavaScript transaction tracers included in go-ethereum.
@@ -571,14 +567,10 @@ func (mo *memoryObj) slice(begin, end int64) ([]byte, error) {
 	if end < begin || begin < 0 {
 		return nil, fmt.Errorf("tracer accessed out of bound memory: offset %d, end %d", begin, end)
 	}
-	mlen := mo.memory.Len()
-	if end-int64(mlen) > memoryPadLimit {
-		return nil, fmt.Errorf("tracer reached limit for padding memory slice: end %d, memorySize %d", end, mlen)
+	slice, err := tracers.GetMemoryCopyPadded(mo.memory, begin, end-begin)
+	if err != nil {
+		return nil, err
 	}
-	slice := make([]byte, end-begin)
-	end = min(end, int64(mo.memory.Len()))
-	ptr := mo.memory.GetPtr(begin, end-begin)
-	copy(slice[:], ptr[:])
 	return slice, nil
 }
 
@@ -959,10 +951,3 @@ func (l *steplog) setupObject() *goja.Object {
 	o.Set("contract", l.contract.setupObject())
 	return o
 }
-
-func min(a, b int64) int64 {
-	if a < b {
-		return a
-	}
-	return b
-}
```

### eth/tracers/js/tracer_test.go
```diff
@@ -150,12 +150,12 @@ func TestTracer(t *testing.T) {
 		}, {
 			code:     "{res: [], step: function(log) { if (log.op.toString() === 'STOP') { this.res.push(log.memory.slice(5, 1025 * 1024)) } }, fault: function() {}, result: function() { return this.res }}",
 			want:     "",
-			fail:     "tracer reached limit for padding memory slice: end 1049600, memorySize 32 at step (<eval>:1:83(20))    in server-side tracer function 'step'",
+			fail:     "reached limit for padding memory slice: 1049568 at step (<eval>:1:83(20))    in server-side tracer function 'step'",
 			contract: []byte{byte(vm.PUSH1), byte(0xff), byte(vm.PUSH1), byte(0x00), byte(vm.MSTORE8), byte(vm.STOP)},
 		},
 	} {
 		if have, err := execTracer(tt.code, tt.contract); tt.want != string(have) || tt.fail != err {
-			t.Errorf("testcase %d: expected return value to be '%s' got '%s', error to be '%s' got '%s'\n\tcode: %v", i, tt.want, string(have), tt.fail, err, tt.code)
+			t.Errorf("testcase %d: expected return value to be \n'%s'\n\tgot\n'%s'\nerror to be\n'%s'\n\tgot\n'%s'\n\tcode: %v", i, tt.want, string(have), tt.fail, err, tt.code)
 		}
 	}
 }
```

### eth/tracers/native/call.go
```diff
@@ -148,6 +148,10 @@ func (t *callTracer) CaptureEnd(output []byte, gasUsed uint64, err error) {
 
 // CaptureState implements the EVMLogger interface to trace a single step of VM execution.
 func (t *callTracer) CaptureState(pc uint64, op vm.OpCode, gas, cost uint64, scope *vm.ScopeContext, rData []byte, depth int, err error) {
+	// skip if the previous op caused an error
+	if err != nil {
+		return
+	}
 	// Only logs need to be captured via opcode processing
 	if !t.config.WithLog {
 		return
@@ -176,7 +180,12 @@ func (t *callTracer) CaptureState(pc uint64, op vm.OpCode, gas, cost uint64, sco
 			topics[i] = common.Hash(topic.Bytes32())
 		}
 
-		data := scope.Memory.GetCopy(int64(mStart.Uint64()), int64(mSize.Uint64()))
+		data, err := tracers.GetMemoryCopyPadded(scope.Memory, int64(mStart.Uint64()), int64(mSize.Uint64()))
+		if err != nil {
+			// mSize was unrealistically large
+			return
+		}
+
 		log := callLog{Address: scope.Contract.Address(), Topics: topics, Data: hexutil.Bytes(data)}
 		t.callstack[len(t.callstack)-1].Logs = append(t.callstack[len(t.callstack)-1].Logs, log)
 	}
```

### eth/tracers/native/prestate.go
```diff
@@ -133,6 +133,9 @@ func (t *prestateTracer) CaptureEnd(output []byte, gasUsed uint64, err error) {
 
 // CaptureState implements the EVMLogger interface to trace a single step of VM execution.
 func (t *prestateTracer) CaptureState(pc uint64, op vm.OpCode, gas, cost uint64, scope *vm.ScopeContext, rData []byte, depth int, err error) {
+	if err != nil {
+		return
+	}
 	stack := scope.Stack
 	stackData := stack.Data()
 	stackLen := len(stackData)
```

### eth/tracers/tracers.go
```diff
@@ -19,6 +19,7 @@ package tracers
 
 import (
 	"encoding/json"
+	"fmt"
 	"math/big"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -95,3 +96,27 @@ func (d *directory) IsJS(name string) bool {
 	// JS eval will execute JS code
 	return true
 }
+
+const (
+	memoryPadLimit = 1024 * 1024
+)
+
+// GetMemoryCopyPadded returns offset + size as a new slice.
+// It zero-pads the slice if it extends beyond memory bounds.
+func GetMemoryCopyPadded(m *vm.Memory, offset, size int64) ([]byte, error) {
+	if offset < 0 || size < 0 {
+		return nil, fmt.Errorf("offset or size must not be negative")
+	}
+	if int(offset+size) < m.Len() { // slice fully inside memory
+		return m.GetCopy(offset, size), nil
+	}
+	paddingNeeded := int(offset+size) - m.Len()
+	if paddingNeeded > memoryPadLimit {
+		return nil, fmt.Errorf("reached limit for padding memory slice: %d", paddingNeeded)
+	}
+	cpy := make([]byte, size)
+	if overlap := int64(m.Len()) - offset; overlap > 0 {
+		copy(cpy, m.GetPtr(offset, overlap))
+	}
+	return cpy, nil
+}
```

### eth/tracers/tracers_test.go
```diff
@@ -109,3 +109,41 @@ func BenchmarkTransactionTrace(b *testing.B) {
 		tracer.Reset()
 	}
 }
+
+func TestMemCopying(t *testing.T) {
+	for i, tc := range []struct {
+		memsize  int64
+		offset   int64
+		size     int64
+		wantErr  string
+		wantSize int
+	}{
+		{0, 0, 100, "", 100},    // Should pad up to 100
+		{0, 100, 0, "", 0},      // No need to pad (0 size)
+		{100, 50, 100, "", 100}, // Should pad 100-150
+		{100, 50, 5, "", 5},     // Wanted range fully within memory
+		{100, -50, 0, "offset or size must not be negative", 0},                        // Errror
+		{0, 1, 1024*1024 + 1, "reached limit for padding memory slice: 1048578", 0},    // Errror
+		{10, 0, 1024*1024 + 100, "reached limit for padding memory slice: 1048666", 0}, // Errror
+
+	} {
+		mem := vm.NewMemory()
+		mem.Resize(uint64(tc.memsize))
+		cpy, err := GetMemoryCopyPadded(mem, tc.offset, tc.size)
+		if want := tc.wantErr; want != "" {
+			if err == nil {
+				t.Fatalf("test %d: want '%v' have no error", i, want)
+			}
+			if have := err.Error(); want != have {
+				t.Fatalf("test %d: want '%v' have '%v'", i, want, have)
+			}
+			continue
+		}
+		if err != nil {
+			t.Fatalf("test %d: unexpected error: %v", i, err)
+		}
+		if want, have := tc.wantSize, len(cpy); have != want {
+			t.Fatalf("test %d: want %v have %v", i, want, have)
+		}
+	}
+}
```
