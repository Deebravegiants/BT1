# [?] Fix tracer nil pointer panic by adding nil checks

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2025-12-17
Source: https://github.com/harmony-one/harmony/commit/949b0c42aebbeaff21219831ab4255dedbe59c19
Type: security-commit

## Details
Fix tracer nil pointer panic by adding nil checks

## Patch
### core/state_transition.go
```diff
@@ -216,7 +216,7 @@ func (st *StateTransition) TransitionDb() (ExecutionResult, error) {
 		return ExecutionResult{}, err
 	}
 
-	if st.evm.Config.Debug {
+	if st.evm.Config.Debug && st.evm.Config.Tracer != nil {
 		st.evm.Config.Tracer.CaptureTxStart(st.initialGas)
 		defer func() {
 			st.evm.Config.Tracer.CaptureTxEnd(st.gas)
```

### core/vm/evm.go
```diff
@@ -302,7 +302,7 @@ func (evm *EVM) Call(caller ContractRef, addr common.Address, input []byte, gas
 	if !evm.StateDB.Exist(addr) {
 		if !isPrecompile && evm.chainRules.IsEIP158 && value.Sign() == 0 {
 			// Calling a non existing account, don't do anything, but ping the tracer
-			if evm.Config.Debug {
+			if evm.Config.Debug && evm.Config.Tracer != nil {
 				if evm.depth == 0 {
 					evm.Config.Tracer.CaptureStart(evm, caller.Address(), addr, false, input, gas, value)
 					evm.Config.Tracer.CaptureEnd(ret, 0, 0, nil)
@@ -318,7 +318,7 @@ func (evm *EVM) Call(caller ContractRef, addr common.Address, input []byte, gas
 	evm.Context.Transfer(evm.StateDB, caller.Address(), addr, value, evm.Context.TxType)
 
 	// Capture the tracer start/end events in debug mode
-	if evm.Config.Debug {
+	if evm.Config.Debug && evm.Config.Tracer != nil {
 		if evm.depth == 0 {
 			evm.Config.Tracer.CaptureStart(evm, caller.Address(), addr, false, input, gas, value)
 			defer func(startGas uint64, startTime time.Time) { // Lazy evaluation of the parameters
@@ -407,7 +407,7 @@ func (evm *EVM) CallCode(caller ContractRef, addr common.Address, input []byte,
 	var snapshot = evm.StateDB.Snapshot()
 
 	// Invoke tracer hooks that signal entering/exiting a call frame
-	if evm.Config.Debug {
+	if evm.Config.Debug && evm.Config.Tracer != nil {
 		evm.Config.Tracer.CaptureEnter(CALLCODE, caller.Address(), addr, input, gas, value)
 		defer func(startGas uint64) {
 			evm.Config.Tracer.CaptureExit(ret, startGas-gas, err)
@@ -466,7 +466,7 @@ func (evm *EVM) DelegateCall(caller ContractRef, addr common.Address, input []by
 	var snapshot = evm.StateDB.Snapshot()
 
 	// Invoke tracer hooks that signal entering/exiting a call frame
-	if evm.Config.Debug {
+	if evm.Config.Debug && evm.Config.Tracer != nil {
 		evm.Config.Tracer.CaptureEnter(DELEGATECALL, caller.Address(), addr, input, gas, nil)
 		defer func(startGas uint64) {
 			evm.Config.Tracer.CaptureExit(ret, startGas-gas, err)
@@ -521,7 +521,7 @@ func (evm *EVM) StaticCall(caller ContractRef, addr common.Address, input []byte
 	evm.StateDB.AddBalance(addr, big0)
 
 	// Invoke tracer hooks that signal entering/exiting a call frame
-	if evm.Config.Debug {
+	if evm.Config.Debug && evm.Config.Tracer != nil {
 		evm.Config.Tracer.CaptureEnter(STATICCALL, caller.Address(), addr, input, gas, nil)
 		defer func(startGas uint64) {
 			evm.Config.Tracer.CaptureExit(ret, startGas-gas, err)
@@ -609,7 +609,7 @@ func (evm *EVM) create(caller ContractRef, codeAndHash *codeAndHash, gas uint64,
 	contract := NewContract(caller, AccountRef(address), value, gas)
 	contract.SetCodeOptionalHash(&address, codeAndHash)
 
-	if evm.Config.Debug {
+	if evm.Config.Debug && evm.Config.Tracer != nil {
 		if evm.depth == 0 {
 			evm.Config.Tracer.CaptureStart(evm, caller.Address(), address, true, codeAndHash.code, gas, value)
 		} else {
@@ -659,7 +659,7 @@ func (evm *EVM) create(caller ContractRef, codeAndHash *codeAndHash, gas uint64,
 	if maxCodeSizeExceeded && err == nil {
 		err = ErrMaxCodeSizeExceeded
 	}
-	if evm.Config.Debug && evm.depth == 0 {
+	if evm.Config.Debug && evm.Config.Tracer != nil && evm.depth == 0 {
 		evm.Config.Tracer.CaptureEnd(ret, gas-contract.Gas, time.Since(start), err)
 	}
 	return ret, address, contract.Gas, err
```

### core/vm/instructions.go
```diff
@@ -843,7 +843,7 @@ func opSelfdestruct(pc *uint64, interpreter *EVMInterpreter, scope *ScopeContext
 	balance := interpreter.evm.StateDB.GetBalance(scope.Contract.Address())
 	interpreter.evm.StateDB.AddBalance(beneficiary.Bytes20(), balance)
 	interpreter.evm.StateDB.Suicide(scope.Contract.Address())
-	if interpreter.cfg.Debug {
+	if interpreter.cfg.Debug && interpreter.cfg.Tracer != nil {
 		interpreter.cfg.Tracer.CaptureEnter(SELFDESTRUCT, scope.Contract.Address(), beneficiary.Bytes20(), []byte{}, 0, balance)
 		interpreter.cfg.Tracer.CaptureExit([]byte{}, 0, nil)
 	}
```

### core/vm/interpreter.go
```diff
@@ -162,7 +162,7 @@ func (in *EVMInterpreter) Run(contract *Contract, input []byte, readOnly bool) (
 
 	if in.cfg.Debug {
 		defer func() {
-			if err != nil {
+			if err != nil && in.cfg.Debug && in.cfg.Tracer != nil {
 				if !logged {
 					in.cfg.Tracer.CaptureState(in.evm, pcCopy, op, gasCopy, cost, callContext, in.returnData, in.evm.depth, err)
 				} else {
@@ -221,14 +221,14 @@ func (in *EVMInterpreter) Run(contract *Contract, input []byte, readOnly bool) (
 				return nil, ErrOutOfGas
 			}
 			// Do tracing before memory expansion
-			if in.cfg.Debug {
+			if in.cfg.Debug && in.cfg.Tracer != nil {
 				in.cfg.Tracer.CaptureState(in.evm, pcCopy, op, gasCopy, cost, callContext, in.returnData, in.evm.depth, err)
 				logged = true
 			}
 			if memorySize > 0 {
 				mem.Resize(memorySize)
 			}
-		} else if in.cfg.Debug {
+		} else if in.cfg.Debug && in.cfg.Tracer != nil {
 			in.cfg.Tracer.CaptureState(in.evm, pcCopy, op, gasCopy, cost, callContext, in.returnData, in.evm.depth, err)
 			logged = true
 		}
```
