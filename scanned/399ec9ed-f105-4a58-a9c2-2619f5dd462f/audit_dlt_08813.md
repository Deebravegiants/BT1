# [?] fix trace, forced batches, decodeTxs overflow, grpc limit #2140 (#2165)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2023-06-06
Source: https://github.com/0xPolygon/zkevm-node/commit/19ed608e330299715fd0075361047f29828052ff
Type: security-commit

## Details
fix trace, forced batches, decodeTxs overflow, grpc limit #2140 (#2165)

## Patch
### docker-compose.yml
```diff
@@ -105,7 +105,7 @@ services:
   zkevm-prover:
     container_name: zkevm-prover
     restart: unless-stopped
-    image: hermeznetwork/zkevm-prover:v1.1.3-fork.4
+    image: hermeznetwork/zkevm-prover:v1.1.4-fork.4
     depends_on:
       zkevm-state-db:
         condition: service_healthy
```

### jsonrpc/endpoints_debug.go
```diff
@@ -211,6 +211,10 @@ func (d *DebugEndpoints) buildStructLogs(stateStructLogs []instrumentation.Struc
 		op := structLog.Op
 		if op == "SHA3" {
 			op = "KECCAK256"
+		} else if op == "STOP" && structLog.Pc == 0 {
+			// this stop is generated for calls with single
+			// step(no depth increase) and must be ignored
+			continue
 		}
 
 		structLogRes := StructLogRes{
```

### state/converters.go
```diff
@@ -142,7 +142,11 @@ func (s *State) convertToProcessTransactionResponse(txs []types.Transaction, res
 		result.Logs = convertToLog(response.Logs)
 		result.ChangesStateRoot = IsStateRootChanged(response.Error)
 		result.ExecutionTrace = *trace
-		result.CallTrace = convertToExecutorTrace(response.CallTrace)
+		callTrace, err := convertToExecutorTrace(response.CallTrace)
+		if err != nil {
+			return nil, err
+		}
+		result.CallTrace = *callTrace
 		result.Tx = txs[i]
 
 		_, err = DecodeTx(common.Bytes2Hex(response.GetRlpTx()))
@@ -256,66 +260,79 @@ func convertToProperMap(responses map[string]string) map[common.Hash]common.Hash
 	return results
 }
 
-func convertToExecutorTrace(callTrace *pb.CallTrace) instrumentation.ExecutorTrace {
+func convertToExecutorTrace(callTrace *pb.CallTrace) (*instrumentation.ExecutorTrace, error) {
 	trace := new(instrumentation.ExecutorTrace)
 	if callTrace != nil {
 		trace.Context = convertToContext(callTrace.Context)
-		trace.Steps = convertToInstrumentationSteps(callTrace.Steps)
+		steps, err := convertToInstrumentationSteps(callTrace.Steps)
+		if err != nil {
+			return nil, err
+		}
+		trace.Steps = steps
 	}
 
-	return *trace
+	return trace, nil
 }
 
 func convertToContext(context *pb.TransactionContext) instrumentation.Context {
 	return instrumentation.Context{
 		Type:         context.Type,
 		From:         context.From,
 		To:           context.To,
-		Input:        string(context.Data),
-		Gas:          fmt.Sprint(context.Gas),
-		Value:        context.Value,
-		Output:       string(context.Output),
+		Input:        context.Data,
+		Gas:          context.Gas,
+		Value:        hex.DecodeBig(context.Value),
+		Output:       context.Output,
 		GasPrice:     context.GasPrice,
-		OldStateRoot: string(context.OldStateRoot),
+		OldStateRoot: common.BytesToHash(context.OldStateRoot),
 		Time:         uint64(context.ExecutionTime),
-		GasUsed:      fmt.Sprint(context.GasUsed),
+		GasUsed:      context.GasUsed,
 	}
 }
 
-func convertToInstrumentationSteps(responses []*pb.TransactionStep) []instrumentation.Step {
+func convertToInstrumentationSteps(responses []*pb.TransactionStep) ([]instrumentation.Step, error) {
 	results := make([]instrumentation.Step, 0, len(responses))
 	for _, response := range responses {
 		step := new(instrumentation.Step)
-		step.StateRoot = string(response.StateRoot)
+		step.StateRoot = common.BytesToHash(response.StateRoot)
 		step.Depth = int(response.Depth)
 		step.Pc = response.Pc
-		step.Gas = fmt.Sprint(response.Gas)
+		step.Gas = response.Gas
 		step.OpCode = fakevm.OpCode(response.Op).String()
 		step.Refund = fmt.Sprint(response.GasRefund)
-		step.Op = fmt.Sprint(response.Op)
+		step.Op = uint64(response.Op)
 		err := executor.RomErr(response.Error)
 		if err != nil {
-			step.Error = err.Error()
+			step.Error = err
 		}
 		step.Contract = convertToInstrumentationContract(response.Contract)
-		step.GasCost = fmt.Sprint(response.GasCost)
-		step.Stack = response.Stack
+		step.GasCost = response.GasCost
+		step.Stack = make([]*big.Int, 0, len(response.Stack))
+		for _, s := range response.Stack {
+			bi, ok := new(big.Int).SetString(s, hex.Base)
+			if !ok {
+				log.Debugf("error while parsing stack valueBigInt")
+				return nil, ErrParsingExecutorTrace
+			}
+			step.Stack = append(step.Stack, bi)
+		}
+
 		step.Memory = make([]byte, len(response.Memory))
 		copy(step.Memory, response.Memory)
 		step.ReturnData = make([]byte, len(response.ReturnData))
 		copy(step.ReturnData, response.ReturnData)
 		results = append(results, *step)
 	}
-	return results
+	return results, nil
 }
 
 func convertToInstrumentationContract(response *pb.Contract) instrumentation.Contract {
 	return instrumentation.Contract{
-		Address: response.Address,
-		Caller:  response.Caller,
-		Value:   response.Value,
-		Input:   string(response.Data),
-		Gas:     fmt.Sprint(response.Gas),
+		Address: common.HexToAddress(response.Address),
+		Caller:  common.HexToAddress(response.Caller),
+		Value:   hex.DecodeBig(response.Value),
+		Input:   response.Data,
+		Gas:     response.Gas,
 	}
 }
 
```

### state/runtime/executor/client.go
```diff
@@ -11,7 +11,7 @@ import (
 	"google.golang.org/grpc/credentials/insecure"
 )
 
-const maxMsgSize = 100000000
+const maxMsgSize = 2 * 1024 * 1024 * 1024
 
 // NewExecutorClient is the executor client constructor.
 func NewExecutorClient(ctx context.Context, c Config) (pb.ExecutorServiceClient, *grpc.ClientConn, context.CancelFunc) {
```

### state/runtime/instrumentation/executortrace.go
```diff
@@ -1,5 +1,11 @@
 package instrumentation
 
+import (
+	"math/big"
+
+	"github.com/ethereum/go-ethereum/common"
+)
+
 // ExecutorTrace contents executor traces.
 type ExecutorTrace struct {
 	Context Context `json:"context"`
@@ -8,48 +14,52 @@ type ExecutorTrace struct {
 
 // Context is the trace context.
 type Context struct {
-	Type     string `json:"type"`
-	From     string `json:"from"`
-	To       string `json:"to"`
-	Input    string `json:"input"`
-	Gas      string `json:"gas"`
-	Value    string `json:"value"`
-	Output   string `json:"output"`
-	Nonce    uint64 `json:"nonce"`
-	GasPrice string `json:"gasPrice"`
-	// ChainID      uint64 `json:"chainId"`
-	OldStateRoot string `json:"oldStateRoot"`
-	Time         uint64 `json:"time"`
-	GasUsed      string `json:"gasUsed"`
+	Type         string      `json:"type"`
+	From         string      `json:"from"`
+	To           string      `json:"to"`
+	Input        []byte      `json:"input"`
+	Gas          uint64      `json:"gas"`
+	Value        *big.Int    `json:"value"`
+	Output       []byte      `json:"output"`
+	Nonce        uint64      `json:"nonce"`
+	GasPrice     string      `json:"gasPrice"`
+	OldStateRoot common.Hash `json:"oldStateRoot"`
+	Time         uint64      `json:"time"`
+	GasUsed      uint64      `json:"gasUsed"`
 }
 
 // Step is a trace step.
 type Step struct {
-	StateRoot  string   `json:"stateRoot"`
-	Depth      int      `json:"depth"`
-	Pc         uint64   `json:"pc"`
-	Gas        string   `json:"gas"`
-	OpCode     string   `json:"opcode"`
-	Refund     string   `json:"refund"`
-	Op         string   `json:"op"`
-	Error      string   `json:"error"`
-	Contract   Contract `json:"contract"`
-	GasCost    string   `json:"gasCost"`
-	Stack      []string `json:"stack"`
-	Memory     []byte   `json:"memory"`
-	ReturnData []byte   `json:"returnData"`
+	StateRoot  common.Hash `json:"stateRoot"`
+	Depth      int         `json:"depth"`
+	Pc         uint64      `json:"pc"`
+	Gas        uint64      `json:"gas"`
+	OpCode     string      `json:"opcode"`
+	Refund     string      `json:"refund"`
+	Op         uint64      `json:"op"`
+	Error      error       `json:"error"`
+	Contract   Contract    `json:"contract"`
+	GasCost    uint64      `json:"gasCost"`
+	Stack      []*big.Int  `json:"stack"`
+	Memory     []byte      `json:"memory"`
+	ReturnData []byte      `json:"returnData"`
 }
 
 // Contract represents a contract in the trace.
 type Contract struct {
-	Address string `json:"address"`
-	Caller  string `json:"caller"`
-	Value   string `json:"value"`
-	Input   string `json:"input"`
-	Gas     string `json:"gas"`
+	Address common.Address `json:"address"`
+	Caller  common.Address `json:"caller"`
+	Value   *big.Int       `json:"value"`
+	Input   []byte         `json:"input"`
+	Gas     uint64         `json:"gas"`
 }
 
 // Tracer represents the executor tracer.
 type Tracer struct {
 	Code string `json:"tracer"`
 }
+
+type InternalTxContext struct {
+	OpCode       string
+	RemainingGas uint64
+}
```

### state/stack.go
```diff
@@ -0,0 +1,44 @@
+package state
+
+import (
+	"errors"
+	"sync"
+)
+
+// ErrStackEmpty returned when Pop is called and the stack is empty
+var ErrStackEmpty = errors.New("Empty Stack")
+
+// Stack is a thread safe stack data structure implementation implementing generics
+type Stack[T any] struct {
+	lock  sync.Mutex
+	items []T
+}
+
+// NewStack creates a new stack
+func NewStack[T any]() *Stack[T] {
+	return &Stack[T]{sync.Mutex{}, make([]T, 0)}
+}
+
+// Push adds an item to the stack
+func (s *Stack[T]) Push(v T) {
+	s.lock.Lock()
+	defer s.lock.Unlock()
+
+	s.items = append(s.items, v)
+}
+
+// Pop removes and returns the last item added to the stack
+func (s *Stack[T]) Pop() (T, error) {
+	s.lock.Lock()
+	defer s.lock.Unlock()
+
+	size := len(s.items)
+	if size == 0 {
+		var r T
+		return r, ErrStackEmpty
+	}
+
+	res := s.items[size-1]
+	s.items = s.items[:size-1]
+	return res, nil
+}
```

### state/transaction.go
```diff
@@ -5,9 +5,8 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"math"
 	"math/big"
-	"strconv"
-	"strings"
 	"time"
 
 	"github.com/0xPolygonHermez/zkevm-node/encoding"
@@ -296,17 +295,6 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 		return nil, err
 	}
 
-	// //save process batch response file
-	// b, err := json.Marshal(processBatchResponse)
-	// if err != nil {
-	// 	return nil, err
-	// }
-	// filePath := "./processBatchResponse.json"
-	// err = os.WriteFile(filePath, b, 0644)
-	// if err != nil {
-	// 	return nil, err
-	// }
-
 	txs, _, err := DecodeTxs(batchL2Data)
 	if err != nil && !errors.Is(err, ErrInvalidData) {
 		return nil, err
@@ -328,6 +316,19 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 		return nil, fmt.Errorf("tx hash not found in executor response")
 	}
 
+	// const path = "/Users/thiago/github.com/0xPolygonHermez/zkevm-node/dist/%v.json"
+	// filePath := fmt.Sprintf(path, "EXECUTOR_processBatchResponse")
+	// c, _ := json.MarshalIndent(processBatchResponse, "", "    ")
+	// os.WriteFile(filePath, c, 0644)
+
+	// filePath = fmt.Sprintf(path, "NODE_execution_trace")
+	// c, _ = json.MarshalIndent(response.ExecutionTrace, "", "    ")
+	// os.WriteFile(filePath, c, 0644)
+
+	// filePath = fmt.Sprintf(path, "NODE_call_trace")
+	// c, _ = json.MarshalIndent(response.CallTrace, "", "    ")
+	// os.WriteFile(filePath, c, 0644)
+
 	result := &runtime.ExecutionResult{
 		CreateAddress: response.CreateAddress,
 		GasLeft:       response.GasLeft,
@@ -350,14 +351,14 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 
 	context := instrumentation.Context{
 		From:         senderAddress.String(),
-		Input:        hex.EncodeToHex(tx.Data()),
-		Gas:          strconv.FormatUint(tx.Gas(), encoding.Base10),
-		Value:        tx.Value().String(),
-		Output:       hex.EncodeToHex(result.ReturnValue),
+		Input:        tx.Data(),
+		Gas:          tx.Gas(),
+		Value:        tx.Value(),
+		Output:       result.ReturnValue,
 		GasPrice:     tx.GasPrice().String(),
-		OldStateRoot: oldStateRoot.String(),
+		OldStateRoot: oldStateRoot,
 		Time:         uint64(endTime.Sub(startTime)),
-		GasUsed:      strconv.FormatUint(result.GasUsed, encoding.Base10),
+		GasUsed:      result.GasUsed,
 	}
 
 	// Fill trace context
@@ -384,33 +385,33 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 		TxHash:      transactionHash,
 	}
 
-	var evmTracer tracers.Tracer
+	var customTracer tracers.Tracer
 	if traceConfig.Is4ByteTracer() {
-		evmTracer, err = native.NewFourByteTracer(tracerContext, traceConfig.TracerConfig)
+		customTracer, err = native.NewFourByteTracer(tracerContext, traceConfig.TracerConfig)
 		if err != nil {
 			log.Errorf("debug transaction: failed to create 4byteTracer, err: %v", err)
 			return nil, fmt.Errorf("failed to create 4byteTracer, err: %v", err)
 		}
 	} else if traceConfig.IsCallTracer() {
-		evmTracer, err = native.NewCallTracer(tracerContext, traceConfig.TracerConfig)
+		customTracer, err = native.NewCallTracer(tracerContext, traceConfig.TracerConfig)
 		if err != nil {
 			log.Errorf("debug transaction: failed to create callTracer, err: %v", err)
 			return nil, fmt.Errorf("failed to create callTracer, err: %v", err)
 		}
 	} else if traceConfig.IsNoopTracer() {
-		evmTracer, err = native.NewNoopTracer(tracerContext, traceConfig.TracerConfig)
+		customTracer, err = native.NewNoopTracer(tracerContext, traceConfig.TracerConfig)
 		if err != nil {
 			log.Errorf("debug transaction: failed to create noopTracer, err: %v", err)
 			return nil, fmt.Errorf("failed to create noopTracer, err: %v", err)
 		}
 	} else if traceConfig.IsPrestateTracer() {
-		evmTracer, err = native.NewPrestateTracer(tracerContext, traceConfig.TracerConfig)
+		customTracer, err = native.NewPrestateTracer(tracerContext, traceConfig.TracerConfig)
 		if err != nil {
 			log.Errorf("debug transaction: failed to create prestateTracer, err: %v", err)
 			return nil, fmt.Errorf("failed to create prestateTracer, err: %v", err)
 		}
 	} else if traceConfig.IsJSCustomTracer() {
-		evmTracer, err = js.NewJsTracer(*traceConfig.Tracer, tracerContext, traceConfig.TracerConfig)
+		customTracer, err = js.NewJsTracer(*traceConfig.Tracer, tracerContext, traceConfig.TracerConfig)
 		if err != nil {
 			log.Errorf("debug transaction: failed to create jsTracer, err: %v", err)
 			return nil, fmt.Errorf("failed to create jsTracer, err: %v", err)
@@ -420,9 +421,9 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 	}
 
 	fakeDB := &FakeDB{State: s, stateRoot: batch.StateRoot.Bytes()}
-	evm := fakevm.NewFakeEVM(fakevm.BlockContext{BlockNumber: big.NewInt(1)}, fakevm.TxContext{GasPrice: gasPrice}, fakeDB, params.TestChainConfig, fakevm.Config{Debug: true, Tracer: evmTracer})
+	evm := fakevm.NewFakeEVM(fakevm.BlockContext{BlockNumber: big.NewInt(1)}, fakevm.TxContext{GasPrice: gasPrice}, fakeDB, params.TestChainConfig, fakevm.Config{Debug: true, Tracer: customTracer})
 
-	traceResult, err := s.ParseTheTraceUsingTheTracer(evm, result.ExecutorTrace, evmTracer)
+	traceResult, err := s.buildTrace(evm, result.ExecutorTrace, customTracer)
 	if err != nil {
 		log.Errorf("debug transaction: failed parse the trace using the tracer: %v", err)
 		return nil, fmt.Errorf("failed parse the trace using the tracer: %v", err)
@@ -434,76 +435,23 @@ func (s *State) DebugTransaction(ctx context.Context, transactionHash common.Has
 }
 
 // ParseTheTraceUsingTheTracer parses the given trace with the given tracer.
-func (s *State) ParseTheTraceUsingTheTracer(evm *fakevm.FakeEVM, trace instrumentation.ExecutorTrace, tracer tracers.Tracer) (json.RawMessage, error) {
-	var previousStep instrumentation.Step
-	var previousOp, previousGas *big.Int
-	var previousError error
-	var stateRoot []byte
-
-	contextGas, ok := new(big.Int).SetString(trace.Context.Gas, encoding.Base10)
-	if !ok {
-		log.Debugf("error while parsing contextGas")
-		return nil, ErrParsingExecutorTrace
-	}
-	value, ok := new(big.Int).SetString(trace.Context.Value, encoding.Base10)
-	if !ok {
-		log.Debugf("error while parsing value")
-		return nil, ErrParsingExecutorTrace
-	}
-
-	tracer.CaptureTxStart(contextGas.Uint64())
-	decodedInput, err := hex.DecodeHex(trace.Context.Input)
-	if err != nil {
-		log.Errorf("error while decoding context input from hex to bytes:, %v", err)
-		return nil, ErrParsingExecutorTrace
-	}
-	tracer.CaptureStart(evm, common.HexToAddress(trace.Context.From), common.HexToAddress(trace.Context.To), trace.Context.Type == "CREATE", decodedInput, contextGas.Uint64(), value)
-
-	bigStateRoot, ok := new(big.Int).SetString(trace.Context.OldStateRoot, 0)
-	if !ok {
-		log.Debugf("error while parsing context oldStateRoot")
-		return nil, ErrParsingExecutorTrace
+func (s *State) buildTrace(evm *fakevm.FakeEVM, trace instrumentation.ExecutorTrace, tracer tracers.Tracer) (json.RawMessage, error) {
+	tracer.CaptureTxStart(trace.Context.Gas)
+	contextGas := trace.Context.Gas - trace.Context.GasUsed
+	if len(trace.Steps) > 0 {
+		contextGas = trace.Steps[0].Gas
 	}
-	stateRoot = bigStateRoot.Bytes()
-	evm.StateDB.SetStateRoot(stateRoot)
+	tracer.CaptureStart(evm, common.HexToAddress(trace.Context.From), common.HexToAddress(trace.Context.To), trace.Context.Type == "CREATE", trace.Context.Input, contextGas, trace.Context.Value)
+	evm.StateDB.SetStateRoot(trace.Context.OldStateRoot.Bytes())
 
-	output := common.FromHex(trace.Context.Output)
-
-	var stepError error
+	var previousStep instrumentation.Step
+	reverted := false
+	internalTxSteps := NewStack[instrumentation.InternalTxContext]()
 	for i, step := range trace.Steps {
-		stepError = nil
-		stepErrorMsg := strings.TrimSpace(step.Error)
-		if stepErrorMsg != "" {
-			stepError = fmt.Errorf(stepErrorMsg)
-		}
-
-		gas, ok := new(big.Int).SetString(step.Gas, encoding.Base10)
-		if !ok {
-			log.Debugf("error while parsing step gas")
-			return nil, ErrParsingExecutorTrace
-		}
-
-		gasCost, ok := new(big.Int).SetString(step.GasCost, encoding.Base10)
-		if !ok {
-			log.Debugf("error while parsing step gasCost")
-			return nil, ErrParsingExecutorTrace
-		}
-
-		op, ok := new(big.Int).SetString(step.Op, 0)
-		if !ok {
-			log.Debugf("error while parsing step op")
-			return nil, ErrParsingExecutorTrace
-		}
-
 		// set Stack
 		stack := fakevm.NewStack()
-		for _, stackContent := range step.Stack {
-			valueBigInt, ok := new(big.Int).SetString(stackContent, hex.Base)
-			if !ok {
-				log.Debugf("error while parsing stack valueBigInt")
-				return nil, ErrParsingExecutorTrace
-			}
-			value, _ := uint256.FromBig(valueBigInt)
+		for _, stackItem := range step.Stack {
+			value, _ := uint256.FromBig(stackItem)
 			stack.Push(value)
 		}
 
@@ -516,40 +464,44 @@ func (s *State) ParseTheTraceUsingTheTracer(evm *fakevm.FakeEVM, trace instrumen
 			memory = fakevm.NewMemory()
 		}
 
+		// set Contract
+		contract := fakevm.NewContract(
+			fakevm.NewAccount(step.Contract.Caller),
+			fakevm.NewAccount(step.Contract.Address),
+			step.Contract.Value, step.Gas)
+		contract.CodeAddr = &step.Contract.Address
+
+		// set Scope
 		scope := &fakevm.ScopeContext{
-			Contract: fakevm.NewContract(fakevm.NewAccount(common.HexToAddress(step.Contract.Caller)), fakevm.NewAccount(common.HexToAddress(step.Contract.Address)), value, gas.Uint64()),
+			Contract: contract,
 			Memory:   memory,
 			Stack:    stack,
 		}
 
-		codeAddr := common.HexToAddress(step.Contract.Address)
-		scope.Contract.CodeAddr = &codeAddr
-
 		// if the revert happens on an internal tx, we exit
 		if previousStep.OpCode == "REVERT" && previousStep.Depth > 1 {
-			stepError = fakevm.ErrExecutionReverted
-			tracer.CaptureExit(step.ReturnData, gasCost.Uint64(), stepError)
+			gasUsed, err := s.getGasUsed(internalTxSteps, previousStep, step)
+			if err != nil {
+				return nil, err
+			}
+			tracer.CaptureExit(step.ReturnData, gasUsed, fakevm.ErrExecutionReverted)
 		}
 
 		// if the revert happens on top level, we break
 		if step.OpCode == "REVERT" && step.Depth == 1 {
-			stepError = fakevm.ErrExecutionReverted
+			reverted = true
 			break
 		}
 
-		if previousStep.OpCode == "CALL" && step.Pc != 0 {
-			tracer.CaptureExit(step.ReturnData, gasCost.Uint64(), stepError)
-		}
-
 		if step.OpCode != "CALL" || trace.Steps[i+1].Pc == 0 {
-			if stepError != nil {
-				tracer.CaptureFault(step.Pc, fakevm.OpCode(op.Uint64()), gas.Uint64(), gasCost.Uint64(), scope, step.Depth, stepError)
+			if step.Error != nil {
+				tracer.CaptureFault(step.Pc, fakevm.OpCode(step.Op), step.Gas, step.GasCost, scope, step.Depth, step.Error)
 			} else {
-				tracer.CaptureState(step.Pc, fakevm.OpCode(op.Uint64()), gas.Uint64(), gasCost.Uint64(), scope, step.ReturnData, step.Depth, nil)
+				tracer.CaptureState(step.Pc, fakevm.OpCode(step.Op), step.Gas, step.GasCost, scope, step.ReturnData, step.Depth, nil)
 			}
 		}
 
-		previousOpCodeCanBeSubCall := previousStep.OpCode == "CREATE" ||
+		previousStepStartedInternalTransaction := previousStep.OpCode == "CREATE" ||
 			previousStep.OpCode == "CREATE2" ||
 			previousStep.OpCode == "DELEGATECALL" ||
 			previousStep.OpCode == "CALL" ||
@@ -558,105 +510,155 @@ func (s *State) ParseTheTraceUsingTheTracer(evm *fakevm.FakeEVM, trace instrumen
 			previousStep.OpCode == "CALLCODE" ||
 			previousStep.OpCode == "SELFDESTRUCT"
 
-		// when a sub call or create is detected, the next step contains the contract updated
-		if previousOpCodeCanBeSubCall {
+		// when an internal transaction is detected, the next step contains the context values
+		if previousStepStartedInternalTransaction {
 			// if the previous depth is the same as the current one, this means
-			// the sub call did not executed any other step and the
+			// the internal transaction did not executed any other step and the
 			// context is back to the same level. This can happen with pre compiled executions.
 			if previousStep.Depth == step.Depth {
-				addr, value, input := s.getInternalTxMemoryValues(previousStep)
-				tracer.CaptureEnter(fakevm.OpCode(previousOp.Uint64()), common.HexToAddress(previousStep.Contract.Address), addr, input, previousGas.Uint64(), value)
-				previousStepGasCost, ok := new(big.Int).SetString(step.GasCost, encoding.Base10)
-				if !ok {
-					log.Debugf("error while parsing previous step gasCost")
-					return nil, ErrParsingExecutorTrace
+				addr, value, input, gas, gasUsed, err := s.getValuesFromInternalTxMemory(internalTxSteps, previousStep, step)
+				if err != nil {
+					return nil, err
+				}
+				from := previousStep.Contract.Address
+				if previousStep.OpCode == "CALL" || previousStep.OpCode == "CALLCODE" {
+					from = previousStep.Contract.Caller
 				}
-				tracer.CaptureExit(step.ReturnData, previousStepGasCost.Uint64(), previousError)
+
+				tracer.CaptureEnter(fakevm.OpCode(previousStep.Op), from, addr, input, gas, value)
+				tracer.CaptureExit(step.ReturnData, gasUsed, previousStep.Error)
 			} else {
-				value := hex.DecodeBig(step.Contract.Value)
+				value := step.Contract.Value
 				if previousStep.OpCode == "STATICCALL" {
 					value = nil
 				}
-				tracer.CaptureEnter(fakevm.OpCode(previousOp.Uint64()), common.HexToAddress(step.Contract.Caller), common.HexToAddress(step.Contract.Address), []byte(step.Contract.Input), previousGas.Uint64(), value)
+				internalTxSteps.Push(instrumentation.InternalTxContext{
+					OpCode:       previousStep.OpCode,
+					RemainingGas: step.Gas,
+				})
+				tracer.CaptureEnter(fakevm.OpCode(previousStep.Op), step.Contract.Caller, step.Contract.Address, step.Contract.Input, step.Gas, value)
 			}
 		}
 
-		// returning from a call or create
+		// returning from internal transaction
 		if previousStep.Depth > step.Depth && previousStep.OpCode != "REVERT" {
-			tracer.CaptureExit(step.ReturnData, gasCost.Uint64(), stepError)
+			gasUsed, err := s.getGasUsed(internalTxSteps, previousStep, step)
+			if err != nil {
+				return nil, err
+			}
+			tracer.CaptureExit(step.ReturnData, gasUsed, step.Error)
 		}
 
 		// set StateRoot
-		stateRoot = []byte(step.StateRoot)
-		evm.StateDB.SetStateRoot(stateRoot)
+		evm.StateDB.SetStateRoot(step.StateRoot.Bytes())
 
-		// set previous step values
+		// set previous step
 		previousStep = step
-		previousOp = op
-		previousGas = gas
-		previousError = stepError
-	}
-
-	gasUsed, ok := new(big.Int).SetString(trace.Context.GasUsed, encoding.Base10)
-	if !ok {
-		log.Debugf("error while parsing gasUsed")
-		return nil, ErrParsingExecutorTrace
 	}
 
-	restGas := contextGas.Uint64() - gasUsed.Uint64()
+	restGas := trace.Context.Gas - trace.Context.GasUsed
 	tracer.CaptureTxEnd(restGas)
-	tracer.CaptureEnd(output, gasUsed.Uint64(), stepError)
+	var err error
+	if reverted {
+		err = fakevm.ErrExecutionReverted
+	}
+	tracer.CaptureEnd(trace.Context.Output, trace.Context.GasUsed, err)
 
 	return tracer.GetResult()
 }
 
-func (s *State) getInternalTxMemoryValues(step instrumentation.Step) (common.Address, *big.Int, []byte) {
-	if step.OpCode == "DELEGATECALL" || step.OpCode == "CALL" || step.OpCode == "STATICCALL" || step.OpCode == "CALLCODE" {
-		gasPos := len(step.Stack) - 1
+func (s *State) getGasUsed(stepStack *Stack[instrumentation.InternalTxContext], previousStep, step instrumentation.Step) (uint64, error) {
+	itCtx, err := stepStack.Pop()
+	if err != nil {
+		return 0, err
+	}
+	var gasUsed uint64
+	if itCtx.OpCode == "CREATE" || itCtx.OpCode == "CREATE2" {
+		// if the context was initialized by a CREATE, we should use the contract gas
+		gasUsed = previousStep.Contract.Gas - step.Gas
+	} else {
+		// otherwise we use the step gas
+		gasUsed = itCtx.RemainingGas - previousStep.Gas - previousStep.GasCost
+	}
+	return gasUsed, nil
+}
+
+func (s *State) getValuesFromInternalTxMemory(stepStack *Stack[instrumentation.InternalTxContext], previousStep, step instrumentation.Step) (common.Address, *big.Int, []byte, uint64, uint64, error) {
+	if previousStep.OpCode == "DELEGATECALL" || previousStep.OpCode == "CALL" || previousStep.OpCode == "STATICCALL" || previousStep.OpCode == "CALLCODE" {
+		gasPos := len(previousStep.Stack) - 1
 		addrPos := gasPos - 1
 
 		argsOffsetPos := addrPos - 1
 		argsSizePos := argsOffsetPos - 1
 
 		// read tx value if it exists
 		var value *big.Int
-		stackHasValue := step.OpCode == "CALL" || step.OpCode == "CALLCODE"
+		stackHasValue := previousStep.OpCode == "CALL" || previousStep.OpCode == "CALLCODE"
 		if stackHasValue {
 			valuePos := addrPos - 1
 			// valueEncoded := step.Stack[valuePos]
 			// value = hex.DecodeBig(valueEncoded)
-			value = hex.DecodeBig(step.Contract.Value)
+			value = previousStep.Contract.Value
 
 			argsOffsetPos = valuePos - 1
 			argsSizePos = argsOffsetPos - 1
 		}
 
-		addrEncoded := step.Stack[addrPos]
-		addr := common.HexToAddress("0x" + addrEncoded)
-
-		argsOffsetEncoded := step.Stack[argsOffsetPos]
-		argsOffset := hex.DecodeUint64(argsOffsetEncoded)
+		retOffsetPos := argsSizePos - 1
+		retSizePos := retOffsetPos - 1
 
-		argsSizeEncoded := step.Stack[argsSizePos]
-		argsSize := hex.DecodeUint64(argsSizeEncoded)
+		addr := common.BytesToAddress(previousStep.Stack[addrPos].Bytes())
+		argsOffset := previousStep.Stack[argsOffsetPos].Uint64()
+		argsSize := previousStep.Stack[argsSizePos].Uint64()
+		retOffset := previousStep.Stack[retOffsetPos].Uint64()
+		retSize := previousStep.Stack[retSizePos].Uint64()
 
 		input := make([]byte, argsSize)
 
-		if argsOffset > uint64(len(step.Memory)) {
+		if argsOffset > uint64(len(previousStep.Memory)) {
 			// when none of the bytes can be found in the memory
 			// do nothing to keep input as zeroes
-		} else if argsOffset+argsSize > uint64(len(step.Memory)) {
+		} else if argsOffset+argsSize > uint64(len(previousStep.Memory)) {
 			// when partial bytes are found in the memory
 			// copy just the bytes we have in memory and complement the rest with zeroes
-			copy(input[0:argsSize], step.Memory[argsOffset:uint64(len(step.Memory))])
+			copy(input[0:argsSize], previousStep.Memory[argsOffset:uint64(len(previousStep.Memory))])
 		} else {
 			// when all the bytes are found in the memory
 			// read the bytes from memory
-			copy(input[0:argsSize], step.Memory[argsOffset:argsOffset+argsSize])
+			copy(input[0:argsSize], previousStep.Memory[argsOffset:argsOffset+argsSize])
 		}
-		return addr, value, input
+
+		// Compute call memory expansion cost
+		memSize := len(previousStep.Memory)
+		lastMemSizeWord := math.Ceil((float64(memSize) + 31) / 32)                          //nolint:gomnd
+		lastMemCost := math.Floor(math.Pow(lastMemSizeWord, 2)/512) + (3 * lastMemSizeWord) //nolint:gomnd
+
+		memSizeWord := math.Ceil((float64(argsOffset+argsSize+31) / 32))                    //nolint:gomnd
+		newMemCost := math.Floor(math.Pow(memSizeWord, float64(2))/512) + (3 * memSizeWord) //nolint:gomnd
+		callMemCost := newMemCost - lastMemCost
+
+		// Compute return memory expansion cost
+		retMemSizeWord := math.Ceil((float64(retOffset) + float64(retSize) + 31) / 32)      //nolint:gomnd
+		retNewMemCost := math.Floor(math.Pow(retMemSizeWord, 2)/512) + (3 * retMemSizeWord) //nolint:gomnd
+		retMemCost := retNewMemCost - newMemCost
+		if retMemCost < 0 {
+			retMemCost = 0
+		}
+
+		callGasCost := retMemCost + callMemCost + 100 //nolint:gomnd
+		gasUsed := float64(previousStep.GasCost) - callGasCost
+
+		// Compute gas sent to call
+		gas := float64(previousStep.Gas) - callGasCost
+		gas -= math.Floor(gas / 64) //nolint:gomnd
+
+		return addr, value, input, uint64(gas), uint64(gasUsed), nil
 	} else {
-		return common.HexToAddress(step.Contract.Address), hex.DecodeBig(step.Contract.Value), []byte(step.Contract.Input)
+		gasUsed, err := s.getGasUsed(stepStack, previousStep, step)
+		if err != nil {
+			return common.Address{}, nil, nil, 0, 0, err
+		}
+		return previousStep.Contract.Address, previousStep.Contract.Value, previousStep.Contract.Input, previousStep.Gas, gasUsed, nil
 	}
 }
 
```

### test/contracts/auto/BridgeA.sol
```diff
@@ -0,0 +1,12 @@
+// SPDX-License-Identifier: GPL-3.0
+pragma solidity >=0.7.0 <0.9.0;
+
+contract BridgeA {
+    receive() external payable {}
+    
+    function exec(address bridgeB, address bridgeC, address bridgeD, address acc) public payable {
+        bool ok;
+        (ok,) = bridgeB.delegatecall(abi.encodeWithSignature("exec(address,address,address)", bridgeC, bridgeD, acc));
+        require(ok, "failed to perform delegate call to bridge B");
+    }
+}
\ No newline at end of file
```

### test/contracts/auto/BridgeB.sol
```diff
@@ -0,0 +1,15 @@
+// SPDX-License-Identifier: GPL-3.0
+pragma solidity >=0.7.0 <0.9.0;
+
+contract BridgeB {
+    receive() external payable {}
+    
+    function exec(address bridgeC, address bridgeD, address acc) public payable {
+        bool ok;
+        (ok,) = bridgeC.call(abi.encodeWithSignature("exec(address)", bridgeD));
+        require(ok, "failed to perform call to bridge C");
+
+        (ok,) = acc.call{value:msg.value}("");
+        require(ok, "failed to perform call to acc");
+    }
+}
```

### test/contracts/auto/BridgeC.sol
```diff
@@ -0,0 +1,12 @@
+// SPDX-License-Identifier: GPL-3.0
+pragma solidity >=0.7.0 <0.9.0;
+
+contract BridgeC {
+    receive() external payable {}
+    
+    function exec(address bridgeD) public payable {
+        bool ok;
+        (ok,) = bridgeD.delegatecall(abi.encodeWithSignature("exec()"));
+        require(ok, "failed to perform delegate call to bridge D");
+    }
+}
```

### test/contracts/auto/BridgeD.sol
```diff
@@ -0,0 +1,14 @@
+// SPDX-License-Identifier: GPL-3.0
+pragma solidity >=0.7.0 <0.9.0;
+
+contract BridgeD {
+    receive() external payable {}
+    
+    address sender;
+    uint256 value;
+
+    function exec() public payable {
+        sender = msg.sender;
+        value = msg.value;
+    }
+}
\ No newline at end of file
```

### test/contracts/auto/ChainCallLevel1.sol
```diff
@@ -2,40 +2,86 @@
 pragma solidity >=0.7.0 <0.9.0;
 
 contract ChainCallLevel1 {
-    function exec(address level2Addr, address level3Addr, address level4Addr) public payable {
+    receive() external payable {}
+
+    function delegateTransfer(
+        address level2Addr,
+        address level3Addr,
+        address level4Addr
+    ) public payable {
+        bool ok;
+        (ok, ) = level2Addr.delegatecall(
+            abi.encodeWithSignature("transfers(address)", level3Addr)
+        );
+        require(ok, "failed to perform delegate call to level 2");
+    }
+
+    function exec(
+        address level2Addr,
+        address level3Addr,
+        address level4Addr
+    ) public payable {
         bool ok;
         (ok, ) = level2Addr.call(
-            abi.encodeWithSignature("exec(address,address)", level3Addr, level4Addr)
+            abi.encodeWithSignature(
+                "exec(address,address)",
+                level3Addr,
+                level4Addr
+            )
         );
         require(ok, "failed to perform call to level 2");
 
         (ok, ) = level2Addr.delegatecall(
-            abi.encodeWithSignature("exec(address,address)", level3Addr, level4Addr)
+            abi.encodeWithSignature(
+                "exec(address,address)",
+                level3Addr,
+                level4Addr
+            )
         );
         require(ok, "failed to perform delegate call to level 2");
 
         bytes memory result;
         (ok, result) = level2Addr.staticcall(
-            abi.encodeWithSignature("get(address,address)", level3Addr, level4Addr)
+            abi.encodeWithSignature(
+                "get(address,address)",
+                level3Addr,
+                level4Addr
+            )
         );
         require(ok, "failed to perform static call to level 2");
 
         string memory t;
         (t) = abi.decode(result, (string));
     }
 
-    function callRevert(address level2Addr, address level3Addr, address level4Addr) public payable {
+    function callRevert(
+        address level2Addr,
+        address level3Addr,
+        address level4Addr
+    ) public payable {
         bool ok;
         (ok, ) = level2Addr.call(
-            abi.encodeWithSignature("callRevert(address,address)", level3Addr, level4Addr)
+            abi.encodeWithSignature(
+                "callRevert(address,address)",
+                level3Addr,
+                level4Addr
+            )
         );
         require(ok, "failed to perform call to level 2");
     }
 
-    function delegateCallRevert(address level2Addr, address level3Addr, address level4Addr) public payable {
+    function delegateCallRevert(
+        address level2Addr,
+        address level3Addr,
+        address level4Addr
+    ) public payable {
         bool ok;
         (ok, ) = level2Addr.delegatecall(
-            abi.encodeWithSignature("delegateCallRevert(address,address)", level3Addr, level4Addr)
+            abi.encodeWithSignature(
+                "delegateCallRevert(address,address)",
+                level3Addr,
+                level4Addr
+            )
         );
         require(ok, "failed to perform delegate call to level 2");
     }
```
