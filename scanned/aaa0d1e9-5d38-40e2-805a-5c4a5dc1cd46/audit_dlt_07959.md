# [?] Prevent panic for LOG edge cases in callTracer (#285)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2023-07-17
Source: https://github.com/ava-labs/avalanchego/commit/e02445701f3379426b2373929aac427c2813e902
Type: security-commit

## Details
Prevent panic for LOG edge cases in callTracer (#285)

* cherry-pick tracer log edge case handling

* Update goja

---------

Co-authored-by: jwasinger <j-wasinger@hotmail.com>

## Patch
### eth/tracers/internal/tracetest/calltrace_test.go
```diff
@@ -44,7 +44,6 @@ import (
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/common/hexutil"
 	"github.com/ethereum/go-ethereum/common/math"
-	"github.com/ethereum/go-ethereum/crypto"
 	"github.com/ethereum/go-ethereum/rlp"
 )
 
@@ -270,75 +269,122 @@ func benchTracer(tracerName string, test *callTracerTest, b *testing.B) {
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
+			BaseFee:     common.Big0,
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
-	evm := vm.NewEVM(context, txContext, statedb, params.AvalancheMainnetChainConfig, vm.Config{Debug: true, Tracer: tracer})
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
+		evm := vm.NewEVM(context, txContext, statedb, params.TestLaunchConfig, vm.Config{Debug: true, Tracer: tc.tracer})
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
@@ -42,10 +42,6 @@ import (
 	"github.com/ethereum/go-ethereum/crypto"
 )
 
-const (
-	memoryPadLimit = 1024 * 1024
-)
-
 var assetTracers = make(map[string]string)
 
 // init retrieves the JavaScript transaction tracers included in go-ethereum.
@@ -581,14 +577,10 @@ func (mo *memoryObj) slice(begin, end int64) ([]byte, error) {
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
 
@@ -969,10 +961,3 @@ func (l *steplog) setupObject() *goja.Object {
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
@@ -160,12 +160,12 @@ func TestTracer(t *testing.T) {
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
@@ -159,6 +159,10 @@ func (t *callTracer) CaptureEnd(output []byte, gasUsed uint64, err error) {
 
 // CaptureState implements the EVMLogger interface to trace a single step of VM execution.
 func (t *callTracer) CaptureState(pc uint64, op vm.OpCode, gas, cost uint64, scope *vm.ScopeContext, rData []byte, depth int, err error) {
+	// skip if the previous op caused an error
+	if err != nil {
+		return
+	}
 	// Only logs need to be captured via opcode processing
 	if !t.config.WithLog {
 		return
@@ -187,7 +191,12 @@ func (t *callTracer) CaptureState(pc uint64, op vm.OpCode, gas, cost uint64, sco
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
@@ -143,6 +143,9 @@ func (t *prestateTracer) CaptureEnd(output []byte, gasUsed uint64, err error) {
 
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
 
 	"github.com/ava-labs/coreth/core/vm"
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
@@ -119,3 +119,41 @@ func BenchmarkTransactionTrace(b *testing.B) {
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

### go.mod
```diff
@@ -9,7 +9,7 @@ require (
 	github.com/cockroachdb/pebble v0.0.0-20230209160836-829675f94811
 	github.com/davecgh/go-spew v1.1.1
 	github.com/deckarep/golang-set/v2 v2.1.0
-	github.com/dop251/goja v0.0.0-20230122112309-96b1610dd4f7
+	github.com/dop251/goja v0.0.0-20230605162241-28ee0ee714f3
 	github.com/ethereum/go-ethereum v1.11.4
 	github.com/fjl/memsize v0.0.0-20190710130421-bcb5799ab5e5
 	github.com/fsnotify/fsnotify v1.6.0
@@ -73,6 +73,7 @@ require (
 	github.com/golang/mock v1.6.0 // indirect
 	github.com/golang/protobuf v1.5.2 // indirect
 	github.com/golang/snappy v0.0.4 // indirect
+	github.com/google/pprof v0.0.0-20230207041349-798e818bf904 // indirect
 	github.com/graph-gophers/graphql-go v1.3.0 // indirect
 	github.com/grpc-ecosystem/go-grpc-prometheus v1.2.0 // indirect
 	github.com/grpc-ecosystem/grpc-gateway/v2 v2.12.0 // indirect
```

### go.sum
```diff
@@ -111,8 +111,11 @@ github.com/cespare/xxhash/v2 v2.1.2/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XL
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
+github.com/chzyer/logex v1.2.0/go.mod h1:9+9sk7u7pGNWYMkh0hdiL++6OeibzJccyQU4p4MedaY=
 github.com/chzyer/readline v0.0.0-20180603132655-2972be24d48e/go.mod h1:nSuG5e5PlCu98SY8svDHJxuZscDgtXS6KTTbou5AhLI=
+github.com/chzyer/readline v1.5.0/go.mod h1:x22KAscuvRqlLoK9CsoYsmxoXZMMFVyOl86cAH8qUic=
 github.com/chzyer/test v0.0.0-20180213035817-a1ea475d72b1/go.mod h1:Q3SI9o4m/ZMnBNeIyt5eFwwo7qiLfzFZmjNmxjkiQlU=
+github.com/chzyer/test v0.0.0-20210722231415-061457976a23/go.mod h1:Q3SI9o4m/ZMnBNeIyt5eFwwo7qiLfzFZmjNmxjkiQlU=
 github.com/client9/misspell v0.3.4/go.mod h1:qj6jICC3Q7zFZvVWo7KLAzC3yx5G7kyvSDkc90ppPyw=
 github.com/cncf/udpa/go v0.0.0-20191209042840-269d4d468f6f/go.mod h1:M8M6+tZqaGXZJjfX53e64911xZQV5JYwmTeXPW+k8Sc=
 github.com/cncf/udpa/go v0.0.0-20200629203442-efcf912fb354/go.mod h1:WmhPx2Nbnhtbo57+VJT5O0JRkEi1Wbu0z5j0R8u5Hbk=
@@ -167,8 +170,8 @@ github.com/dlclark/regexp2 v1.7.0 h1:7lJfhqlPssTb1WQx4yvTHN0uElPEv52sbaECrAQxjAo
 github.com/dlclark/regexp2 v1.7.0/go.mod h1:DHkYz0B9wPfa6wondMfaivmHpzrQ3v9q8cnmRbL6yW8=
 github.com/docker/docker v1.6.2 h1:HlFGsy+9/xrgMmhmN+NGhCc5SHGJ7I+kHosRR1xc/aI=
 github.com/dop251/goja v0.0.0-20211022113120-dc8c55024d06/go.mod h1:R9ET47fwRVRPZnOGvHxxhuZcbrMCuiqOz3Rlrh4KSnk=
-github.com/dop251/goja v0.0.0-20230122112309-96b1610dd4f7 h1:kgvzE5wLsLa7XKfV85VZl40QXaMCaeFtHpPwJ8fhotY=
-github.com/dop251/goja v0.0.0-20230122112309-96b1610dd4f7/go.mod h1:yRkwfj0CBpOGre+TwBsqPV0IH0Pk73e4PXJOeNDboGs=
+github.com/dop251/goja v0.0.0-20230605162241-28ee0ee714f3 h1:+3HCtB74++ClLy8GgjUQYeC8R4ILzVcIe8+5edAJJnE=
+github.com/dop251/goja v0.0.0-20230605162241-28ee0ee714f3/go.mod h1:QMWlm50DNe14hD7t24KEqZuUdC9sOTy8W6XbCU1mlw4=
 github.com/dop251/goja_nodejs v0.0.0-20210225215109-d91c329300e7/go.mod h1:hn7BA7c8pLvoGndExHudxTDKZ84Pyvv+90pbBjbTz0Y=
 github.com/dop251/goja_nodejs v0.0.0-20211022123610-8dd9abb0616d/go.mod h1:DngW8aVqWbuLRMHItjPUyqdj+HWPvnQe8V8y1nDpIbM=
 github.com/dustin/go-humanize v1.0.0/go.mod h1:HtrtbFcZ19U5GC7JDqmcUSB87Iq5E25KnS6fMYU6eOk=
@@ -326,6 +329,8 @@ github.com/google/pprof v0.0.0-20201023163331-3e6fc7fc9c4c/go.mod h1:kpwsk12EmLe
 github.com/google/pprof v0.0.0-20201203190320-1bf35d6f28c2/go.mod h1:kpwsk12EmLew5upagYY7GY0pfYCcupk39gWOCRROcvE=
 github.com/google/pprof v0.0.0-20201218002935-b9804c9f04c2/go.mod h1:kpwsk12EmLew5upagYY7GY0pfYCcupk39gWOCRROcvE=
 github.com/google/pprof v0.0.0-20210407192527-94a9f03dee38/go.mod h1:kpwsk12EmLew5upagYY7GY0pfYCcupk39gWOCRROcvE=
+github.com/google/pprof v0.0.0-20230207041349-798e818bf904 h1:4/hN5RUoecvl+RmJRE2YxKWtnnQls6rQjjW5oV7qg2U=
+github.com/google/pprof v0.0.0-20230207041349-798e818bf904/go.mod h1:uglQLonpP8qtYCYyzA+8c/9qtqgA3qsXGYqCPKARAFg=
 github.com/google/renameio v0.1.0/go.mod h1:KWCgfxg9yswjAJkECMjeO8J8rahYeXnNhOm40UhjYkI=
 github.com/google/uuid v1.1.2/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
 github.com/google/uuid v1.3.0 h1:t6JiXgmwXMjEs8VusXIJk2BXHsn+wx8BZdTaoZ5fu7I=
@@ -370,6 +375,7 @@ github.com/huin/goutil v0.0.0-20170803182201-1ca381bf3150/go.mod h1:PpLOETDnJ0o3
 github.com/hydrogen18/memlistener v0.0.0-20200120041712-dcc25e7acd91/go.mod h1:qEIFzExnS6016fRpRfxrExeVn2gbClQA99gQhnIcdhE=
 github.com/ianlancetaylor/demangle v0.0.0-20181102032728-5e5cf60278f6/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
 github.com/ianlancetaylor/demangle v0.0.0-20200824232613-28f6c0f3b639/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
+github.com/ianlancetaylor/demangle v0.0.0-20220319035150-800ac71e25c2/go.mod h1:aYm2/VgdVmcIU8iMfdMvDMsRAQjcfZSKFby6HOFvi/w=
 github.com/imkira/go-interpol v1.1.0/go.mod h1:z0h2/2T3XF8kyEPpRgJ3kmNv+C43p+I/CoI+jC3w2iA=
 github.com/inconshreveable/mousetrap v1.0.0/go.mod h1:PxqpIevigyE2G7u3NXJIT2ANytuPF1OarO4DADm73n8=
 github.com/influxdata/flux v0.65.1/go.mod h1:J754/zds0vvpfwuq7Gc2wRdVwEodfpCFM7mYlOw2LqY=
@@ -664,6 +670,7 @@ github.com/yuin/goldmark v1.1.27/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9de
 github.com/yuin/goldmark v1.1.32/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.2.1/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.3.5/go.mod h1:mwnBkeHKe2W/ZEtQ+71ViKU8L12m81fl3OWwC1Zlc8k=
+github.com/yuin/goldmark v1.4.13/go.mod h1:6yULJ656Px+3vBD8DxQVa3kxgyrAnzto9xy5taEt/CY=
 github.com/yusufpapurcu/wmi v1.2.2 h1:KBNDSne4vP5mbSWnJbO+51IMOXJB67QiYCSBrubbPRg=
 github.com/yusufpapurcu/wmi v1.2.2/go.mod h1:SBZ9tNy3G9/m5Oi98Zks0QjeHVDvuK0qfxQmPyzfmi0=
 go.opencensus.io v0.21.0/go.mod h1:mSImk1erAIZhrmZN+AvHh14ztQfjbGwt4TtuofqLduU=
@@ -760,6 +767,7 @@ golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
+golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
 golang.org/x/net v0.0.0-20180719180050-a680a1efc54d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -806,6 +814,7 @@ golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT
 golang.org/x/net v0.0.0-20211008194852-3b03d305991f/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
 golang.org/x/net v0.7.0 h1:rJrUqqhjsgNp7KqAIc25s9pZnjU7TUcSY7HcVZjdn1g=
 golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -829,6 +838,7 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
+golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.1.0 h1:wsuoTGHzEhffawBOhz5CYhcrV4IdKZbEyZjBMuTp12o=
 golang.org/x/sync v0.1.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -894,9 +904,11 @@ golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20211007075335-d3039528d8ac/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220209214540-3681064d5158/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220310020820-b874c991c1a5/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220405052023-b1e9470b6e64/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
@@ -915,6 +927,7 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
 golang.org/x/text v0.7.0 h1:4BRB4x83lYWy72KwLD/qYDuTu7q9PjSagHvijDw7cLo=
 golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -983,6 +996,7 @@ golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
 golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
+golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
```
