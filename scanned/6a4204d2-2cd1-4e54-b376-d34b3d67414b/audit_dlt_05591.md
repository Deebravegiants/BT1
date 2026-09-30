# [?] core: fix tracer panic (#35396)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-07-22
Source: https://github.com/ethereum/go-ethereum/commit/5d88c6b324b69f391e2677f13e5eae4493eefb4b
Type: security-commit

## Details
core: fix tracer panic (#35396)

Now with 8037, there are transactions that fail AFTER intrinsic gas but
BEFORE Call or Create operation. These will currently result in a panic
in tracing, since they produce a receipt

---------

Co-authored-by: Gary Rong <garyrong0905@gmail.com>

## Patch
### core/eip8037_test.go
```diff
@@ -109,6 +109,11 @@ func mkCommittedState(t *testing.T, alloc types.GenesisAlloc) *state.StateDB {
 
 // amsterdamCoreEVM builds an Amsterdam EVM over statedb with fees disabled.
 func amsterdamCoreEVM(sdb *state.StateDB) *vm.EVM {
+	return amsterdamTracedEVM(sdb, nil)
+}
+
+// amsterdamTracedEVM is amsterdamCoreEVM with tracing hooks attached.
+func amsterdamTracedEVM(sdb *state.StateDB, hooks *tracing.Hooks) *vm.EVM {
 	ctx := vm.BlockContext{
 		CanTransfer:      CanTransfer,
 		Transfer:         Transfer,
@@ -121,7 +126,7 @@ func amsterdamCoreEVM(sdb *state.StateDB) *vm.EVM {
 		GasLimit:         60_000_000,
 		CostPerStateByte: params.CostPerStateByte,
 	}
-	return vm.NewEVM(ctx, sdb, cfg8037, vm.Config{NoBaseFee: true})
+	return vm.NewEVM(ctx, sdb, cfg8037, vm.Config{NoBaseFee: true, Tracer: hooks})
 }
 
 // applyMsg applies one transaction with a fresh block gas pool and returns the
@@ -481,6 +486,64 @@ func TestCreate2StorageOnlyDestPrechargeOOG(t *testing.T) {
 	}
 }
 
+// A transaction halting on the pre-frame runtime charges never enters the
+// EVM, but tracers assume every receipt-producing transaction emits a
+// depth-zero frame (e.g. callTracer indexes callstack[0] in OnTxEnd). The
+// state transition must synthesize the top-frame enter/exit pair.
+func TestPrechargeOOGEmitsTopFrame(t *testing.T) {
+	// Both gas limits pass intrinsic validation but cannot cover the 183,600
+	// account-creation state charge applied before the top frame is entered.
+	cases := []struct {
+		name string
+		tx   *types.Transaction
+		typ  vm.OpCode
+	}{
+		{"transfer-to-empty", callTx(0, common.HexToAddress("0xc0ffee"), 1, 60_000, nil), vm.CALL},
+		{"create", createTx(0, 100_000, deploy3), vm.CREATE},
+	}
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			type frame struct {
+				depth int
+				typ   byte
+				err   error
+			}
+			var enters, exits []frame
+			hooks := &tracing.Hooks{
+				OnEnter: func(depth int, typ byte, from, to common.Address, input []byte, gas uint64, value *big.Int) {
+					enters = append(enters, frame{depth: depth, typ: typ})
+				},
+				OnExit: func(depth int, output []byte, gasUsed uint64, err error, reverted bool) {
+					exits = append(exits, frame{depth: depth, err: err})
+				},
+			}
+			sdb := mkState(senderAlloc(nil))
+			evm := amsterdamTracedEVM(sdb, hooks)
+			msg, err := TransactionToMessage(tc.tx, signer8037, evm.Context.BaseFee)
+			if err != nil {
+				t.Fatalf("to message: %v", err)
+			}
+			evm.SetTxContext(NewEVMTxContext(msg))
+			res, err := newStateTransition(evm, msg, NewGasPool(evm.Context.GasLimit)).execute()
+			if err != nil {
+				t.Fatal(err)
+			}
+			if !res.Failed() || !errors.Is(res.Err, vm.ErrOutOfGas) {
+				t.Fatalf("err = %v, want out of gas before the top frame", res.Err)
+			}
+			if len(enters) != 1 || len(exits) != 1 {
+				t.Fatalf("got %d enter / %d exit events, want exactly one of each", len(enters), len(exits))
+			}
+			if enters[0].depth != 0 || enters[0].typ != byte(tc.typ) {
+				t.Fatalf("enter = depth %d type %#x, want depth 0 type %#x", enters[0].depth, enters[0].typ, byte(tc.typ))
+			}
+			if exits[0].depth != 0 || !errors.Is(exits[0].err, vm.ErrOutOfGas) {
+				t.Fatalf("exit = depth %d err %v, want depth 0 out of gas", exits[0].depth, exits[0].err)
+			}
+		})
+	}
+}
+
 // ======================== Transaction validation =========================
 
 // The regular dimension must have room for min(tx.gas, MaxTxGas).
```

### core/state_transition.go
```diff
@@ -510,6 +510,7 @@ func (st *stateTransition) initRuntimeGasBudget(rules params.Rules, intrinsicGas
 	st.gasRemaining = vm.NewGasBudget(gasLeft, executionGas-gasLeft)
 
 	if st.evm.Config.Tracer.HasGasHook() {
+		st.evm.Config.Tracer.EmitGasChange(tracing.Gas{}, tracing.Gas{Regular: st.msg.GasLimit}, tracing.GasChangeTxInitialBalance)
 		st.evm.Config.Tracer.EmitGasChange(tracing.Gas{Regular: st.msg.GasLimit}, st.gasRemaining.AsTracing(), tracing.GasChangeTxIntrinsicGas)
 	}
 }
@@ -792,7 +793,10 @@ func (st *stateTransition) executeCreate(rules params.Rules, value *uint256.Int)
 				// The nonce increment normally performed inside evm.Create
 				// must still happen for the included transaction.
 				st.state.SetNonce(msg.From, st.state.GetNonce(msg.From)+1, tracing.NonceChangeContractCreator)
+
+				entryGas := st.gasRemaining
 				st.gasRemaining = st.gasRemaining.ExitHalt()
+				st.traceHaltedTopFrame(vm.CREATE, addr, msg.Data, entryGas, st.gasRemaining, value)
 				return nil, vm.ErrOutOfGas
 			}
 			chargedCreation = true
@@ -829,14 +833,17 @@ func (st *stateTransition) executeCall(rules params.Rules, value *uint256.Int) (
 
 	if rules.IsAmsterdam {
 		snapshot := st.state.Snapshot()
+		entryGas := st.gasRemaining
 		if !st.applyAuthorizations(rules, st.msg.SetCodeAuthorizations) {
 			st.state.RevertToSnapshot(snapshot)
 			st.gasRemaining = st.gasRemaining.ExitHalt()
+			st.traceHaltedTopFrame(vm.CALL, st.to(), msg.Data, entryGas, st.gasRemaining, value)
 			return nil, vm.ErrOutOfGas
 		}
 		if !st.chargeCallRecipientEIP2780(value) {
 			st.state.RevertToSnapshot(snapshot)
 			st.gasRemaining = st.gasRemaining.ExitHalt()
+			st.traceHaltedTopFrame(vm.CALL, st.to(), msg.Data, entryGas, st.gasRemaining, value)
 			return nil, vm.ErrOutOfGas
 		}
 	} else {
@@ -871,6 +878,26 @@ func (st *stateTransition) executeCall(rules params.Rules, value *uint256.Int) (
 	return ret, vmerr
 }
 
+// traceHaltedTopFrame calls the Enter and Exit functions on the tracer,
+// in order to produce correct tracing results if the EVM exits early (after Amsterdam).
+// Tracers assume every transaction producing a receipt also produces a depth-zero frame.
+func (st *stateTransition) traceHaltedTopFrame(typ vm.OpCode, to common.Address, input []byte, entryGas vm.GasBudget, endGas vm.GasBudget, value *uint256.Int) {
+	tracer := st.evm.Config.Tracer
+	if tracer == nil {
+		return
+	}
+	if tracer.OnEnter != nil {
+		tracer.OnEnter(0, byte(typ), st.msg.From, to, input, entryGas.RegularGas, value.ToBig())
+	}
+	if tracer.HasGasHook() {
+		tracer.EmitGasChange(tracing.Gas{}, entryGas.AsTracing(), tracing.GasChangeCallInitialBalance)
+		tracer.EmitGasChange(entryGas.AsTracing(), endGas.AsTracing(), tracing.GasChangeCallFailedExecution)
+	}
+	if tracer.OnExit != nil {
+		tracer.OnExit(0, nil, entryGas.RegularGas, vm.VMErrorFromErr(vm.ErrOutOfGas), true)
+	}
+}
+
 // chargeRuntimeGas deducts an EIP-2780 runtime charge from the transaction's
 // gas budget and reports whether the budget covered it.
 func (st *stateTransition) chargeRuntimeGas(cost vm.GasCosts) bool {
```

### core/tracing/hooks.go
```diff
@@ -165,34 +165,20 @@ type (
 	FaultHook = func(pc uint64, op byte, gas, cost uint64, scope OpContext, depth int, err error)
 
 	// GasChangeHook reports changes to the regular execution gas. Tracers
-	// that don't need visibility into the state-access gas dimension
-	// introduced by EIP-8037 (Amsterdam) can implement only this hook; it
-	// will continue to fire across the Amsterdam fork unchanged.
-	//
-	// If both this hook and GasChangeHookV2 are implemented on the same
-	// tracer, only V2 will be invoked. Implement exactly one to avoid
-	// double-counting.
+	// that don't need the EIP-8037 (Amsterdam) state-access dimension can
+	// implement only this hook; it fires unchanged across the fork. If both
+	// this and GasChangeHookV2 are set, only V2 is invoked; implement exactly
+	// one to avoid double-counting.
 	GasChangeHook = func(old, new uint64, reason GasChangeReason)
 
-	// GasChangeHookV2 is invoked when any gas dimension changes. It is the
-	// multi-dimensional successor to GasChangeHook, exposing the state-access
-	// gas dimension introduced by EIP-8037 (Amsterdam) alongside the regular
-	// dimension.
-	//
-	// Compatibility:
-	//   - Post-Amsterdam: fires for changes to either the regular or the
-	//     state-access dimension. The non-changing dimension is passed through
-	//     unchanged in both `old` and `new` so consumers always observe the
-	//     complete gas vector.
-	//   - Pre-Amsterdam: no state-access gas events occur, so the State field
-	//     of both `old` and `new` is always zero. Tracers that register only
-	//     V2 still receive every regular-gas change as Gas{State: 0} and
-	//     behave identically to a V1 tracer; there is no pre-Amsterdam event
-	//     a V2-only tracer misses.
-	//
-	// V1 and V2 coexist: when both are registered on a tracer, only V2 is
-	// invoked. Tracers SHOULD register at most one of the two to avoid
-	// double-counting.
+	// GasChangeHookV2 is the multi-dimensional successor to GasChangeHook,
+	// invoked when any gas dimension changes and exposing the EIP-8037
+	// (Amsterdam) state-access dimension alongside the regular one. The
+	// non-changing dimension is passed through unchanged in both `old` and
+	// `new`, so consumers always see the complete gas vector. Pre-Amsterdam
+	// the State field is always zero, making a V2-only tracer behave exactly
+	// like a V1 one. If both hooks are set, only V2 is invoked; register at
+	// most one to avoid double-counting.
 	GasChangeHookV2 = func(old, new Gas, reason GasChangeReason)
 
 	/*
@@ -220,15 +206,14 @@ type (
 	// GenesisBlockHook is called when the genesis block is being processed.
 	GenesisBlockHook = func(genesis *types.Block, alloc types.GenesisAlloc)
 
-	// OnSystemCallStartHook is called when a system call is about to be executed. Today,
-	// this hook is invoked when the EIP-4788 system call is about to be executed to set the
-	// beacon block root.
+	// OnSystemCallStartHook is called when a system call is about to be executed.
 	//
-	// After this hook, the EVM call tracing will happened as usual so you will receive a `OnEnter/OnExit`
-	// as well as state hooks between this hook and the `OnSystemCallEndHook`.
+	// After this hook, the EVM call tracing will happened as usual so you will
+	// receive a `OnEnter/OnExit` as well as state hooks between this hook and the
+	// `OnSystemCallEndHook`.
 	//
-	// Note that system call happens outside normal transaction execution, so the `OnTxStart/OnTxEnd` hooks
-	// will not be invoked.
+	// Note that system call happens outside normal transaction execution, so the
+	// `OnTxStart/OnTxEnd` hooks will not be invoked.
 	OnSystemCallStartHook = func()
 
 	// OnSystemCallStartHookV2 is called when a system call is about to be executed. Refer
@@ -348,46 +333,59 @@ const (
 	// Issuance
 	// BalanceIncreaseRewardMineUncle is a reward for mining an uncle block.
 	BalanceIncreaseRewardMineUncle BalanceChangeReason = 1
+
 	// BalanceIncreaseRewardMineBlock is a reward for mining a block.
 	BalanceIncreaseRewardMineBlock BalanceChangeReason = 2
+
 	// BalanceIncreaseWithdrawal is ether withdrawn from the beacon chain.
 	BalanceIncreaseWithdrawal BalanceChangeReason = 3
+
 	// BalanceIncreaseGenesisBalance is ether allocated at the genesis block.
 	BalanceIncreaseGenesisBalance BalanceChangeReason = 4
 
 	// Transaction fees
-	// BalanceIncreaseRewardTransactionFee is the transaction tip increasing block builder's balance.
+	// BalanceIncreaseRewardTransactionFee is the transaction tip increasing
+	// block builder's balance.
 	BalanceIncreaseRewardTransactionFee BalanceChangeReason = 5
-	// BalanceDecreaseGasBuy is spent to purchase gas for execution a transaction.
-	// Part of this gas will be burnt as per EIP-1559 rules.
+
+	// BalanceDecreaseGasBuy is ether spent to purchase gas for a transaction,
+	// part of which is burnt under EIP-1559.
 	BalanceDecreaseGasBuy BalanceChangeReason = 6
-	// BalanceIncreaseGasReturn is ether returned for unused gas at the end of execution.
+
+	// BalanceIncreaseGasReturn is ether returned for unused gas at the end
+	// of execution.
 	BalanceIncreaseGasReturn BalanceChangeReason = 7
 
 	// DAO fork
 	// BalanceIncreaseDaoContract is ether sent to the DAO refund contract.
 	BalanceIncreaseDaoContract BalanceChangeReason = 8
-	// BalanceDecreaseDaoAccount is ether taken from a DAO account to be moved to the refund contract.
+
+	// BalanceDecreaseDaoAccount is ether taken from a DAO account to be moved
+	// to the refund contract.
 	BalanceDecreaseDaoAccount BalanceChangeReason = 9
 
-	// BalanceChangeTransfer is ether transferred via a call.
-	// it is a decrease for the sender and an increase for the recipient.
+	// BalanceChangeTransfer is ether transferred via a call: a decrease for the
+	// sender and an increase for the recipient.
 	BalanceChangeTransfer BalanceChangeReason = 10
-	// BalanceChangeTouchAccount is a transfer of zero value. It is only there to
-	// touch-create an account.
+
+	// BalanceChangeTouchAccount is a zero-value transfer that only touch-creates
+	// an account.
 	BalanceChangeTouchAccount BalanceChangeReason = 11
 
-	// BalanceIncreaseSelfdestruct is added to the recipient as indicated by a selfdestructing account.
+	// BalanceIncreaseSelfdestruct is added to the recipient as indicated by a
+	// selfdestructing account.
 	BalanceIncreaseSelfdestruct BalanceChangeReason = 12
+
 	// BalanceDecreaseSelfdestruct is deducted from a contract due to self-destruct.
 	BalanceDecreaseSelfdestruct BalanceChangeReason = 13
-	// BalanceDecreaseSelfdestructBurn is ether that is sent to an already self-destructed
-	// account within the same tx (captured at end of tx).
-	// Note it doesn't account for a self-destruct which appoints itself as recipient.
+
+	// BalanceDecreaseSelfdestructBurn is ether sent to an account already
+	// self-destructed within the same tx (captured at end of tx). It excludes a
+	// self-destruct that appoints itself as recipient.
 	BalanceDecreaseSelfdestructBurn BalanceChangeReason = 14
 
-	// BalanceChangeRevert is emitted when the balance is reverted back to a previous value due to call failure.
-	// It is only emitted when the tracer has opted in to use the journaling wrapper (WrapWithJournal).
+	// BalanceChangeRevert reverts the balance to a previous value on call
+	// failure. Emitted only when the tracer opts into WrapWithJournal.
 	BalanceChangeRevert BalanceChangeReason = 15
 )
 
@@ -407,86 +405,108 @@ type Gas struct {
 // GasChangeReason is used to indicate the reason for a gas change, useful
 // for tracing and reporting.
 //
-// There is essentially two types of gas changes, those that can be emitted once per transaction
-// and those that can be emitted on a call basis, so possibly multiple times per transaction.
+// There is essentially two types of gas changes, those that can be emitted once
+// per transaction and those that can be emitted on a call basis, so possibly
+// multiple times per transaction.
 //
-// They can be recognized easily by their name, those that start with `GasChangeTx` are emitted
-// once per transaction, while those that start with `GasChangeCall` are emitted on a call basis.
+// They can be recognized easily by their name, those that start with `GasChangeTx`
+// are emitted once per transaction, while those that start with `GasChangeCall`
+// are emitted on a call basis.
 type GasChangeReason byte
 
 //go:generate go run golang.org/x/tools/cmd/stringer -type=GasChangeReason -trimprefix=GasChange -output gen_gas_change_reason_stringer.go
 
 const (
 	GasChangeUnspecified GasChangeReason = 0
 
-	// GasChangeTxInitialBalance is the initial balance for the call which will be equal to the gasLimit of the call. There is only
-	// one such gas change per transaction.
+	// GasChangeTxInitialBalance is the tx's initial balance, equal to its gas
+	// limit. At most one per transaction.
 	GasChangeTxInitialBalance GasChangeReason = 1
-	// GasChangeTxIntrinsicGas is the amount of gas that will be charged for the intrinsic cost of the transaction, there is
-	// always exactly one of those per transaction.
+
+	// GasChangeTxIntrinsicGas is the intrinsic cost of the transaction. Exactly
+	// one per transaction.
 	GasChangeTxIntrinsicGas GasChangeReason = 2
-	// GasChangeTxRefunds is the sum of all refunds which happened during the tx execution (e.g. storage slot being cleared)
-	// this generates an increase in gas. There is at most one of such gas change per transaction.
+
+	// GasChangeTxRefunds is the sum of all refunds accrued during execution
+	// (e.g. a storage slot being cleared), an increase. At most one per tx.
 	GasChangeTxRefunds GasChangeReason = 3
-	// GasChangeTxLeftOverReturned is the amount of gas left over at the end of transaction's execution that will be returned
-	// to the account. This change will always be a negative change as we "drain" left over gas towards 0. If there was no gas
-	// left at the end of execution, no such even will be emitted. The returned gas's value in Wei is returned to caller.
-	// There is at most one of such gas change per transaction.
+
+	// GasChangeTxLeftOverReturned is the gas left at the end of the transaction,
+	// returned to the account (its Wei value refunded to the caller). Always a
+	// decrease towards 0; not emitted when no gas is left. At most one per tx.
 	GasChangeTxLeftOverReturned GasChangeReason = 4
 
-	// GasChangeCallInitialBalance is the initial balance for the call which will be equal to the gasLimit of the call. There is only
-	// one such gas change per call.
+	// GasChangeCallInitialBalance is the initial balance of a call, equal to its
+	// gas limit. At most one per call.
 	GasChangeCallInitialBalance GasChangeReason = 5
-	// GasChangeCallLeftOverReturned is the amount of gas left over that will be returned to the caller, this change will always
-	// be a negative change as we "drain" left over gas towards 0. If there was no gas left at the end of execution, no such even
-	// will be emitted.
+
+	// GasChangeCallLeftOverReturned is the gas left over that is returned to the
+	// caller. Always a decrease towards 0; not emitted when no gas is left.
 	GasChangeCallLeftOverReturned GasChangeReason = 6
-	// GasChangeCallLeftOverRefunded is the amount of gas that will be refunded to the call after the child call execution it
-	// executed completed. This value is always positive as we are giving gas back to the you, the left over gas of the child.
-	// If there was no gas left to be refunded, no such even will be emitted.
+
+	// GasChangeCallLeftOverRefunded is the child call's left-over gas given back
+	// to the caller. Always an increase; not emitted when nothing is refunded.
 	GasChangeCallLeftOverRefunded GasChangeReason = 7
-	// GasChangeCallContractCreation is the amount of gas that will be burned for a CREATE.
+
+	// GasChangeCallContractCreation is the gas burned for a CREATE.
 	GasChangeCallContractCreation GasChangeReason = 8
-	// GasChangeCallContractCreation2 is the amount of gas that will be burned for a CREATE2.
+
+	// GasChangeCallContractCreation2 is the gas burned for a CREATE2.
 	GasChangeCallContractCreation2 GasChangeReason = 9
-	// GasChangeCallCodeStorage is the amount of gas that will be charged for code storage.
+
+	// GasChangeCallCodeStorage is the gas charged for code storage.
 	GasChangeCallCodeStorage GasChangeReason = 10
-	// GasChangeCallOpCode is the amount of gas that will be charged for an opcode executed by the EVM, exact opcode that was
-	// performed can be check by `OnOpcode` handling.
+
+	// GasChangeCallOpCode is the gas charged for an executed opcode; the exact
+	// opcode is available via OnOpcode.
 	GasChangeCallOpCode GasChangeReason = 11
-	// GasChangeCallPrecompiledContract is the amount of gas that will be charged for a precompiled contract execution.
+
+	// GasChangeCallPrecompiledContract is the gas charged for a precompile.
 	GasChangeCallPrecompiledContract GasChangeReason = 12
-	// GasChangeCallStorageColdAccess is the amount of gas that will be charged for a cold storage access as controlled by EIP2929 rules.
+
+	// GasChangeCallStorageColdAccess is the gas charged for a cold storage
+	// access under EIP-2929.
 	GasChangeCallStorageColdAccess GasChangeReason = 13
-	// GasChangeCallFailedExecution is the burning of the remaining gas when the execution failed without a revert.
+
+	// GasChangeCallFailedExecution is the remaining gas burned when execution
+	// fails without a revert.
 	GasChangeCallFailedExecution GasChangeReason = 14
-	// GasChangeWitnessContractInit flags the event of adding to the witness during the contract creation initialization step.
+
+	// GasChangeWitnessContractInit flags a witness addition during the contract
+	// creation initialization step.
 	GasChangeWitnessContractInit GasChangeReason = 15
-	// GasChangeWitnessContractCreation flags the event of adding to the witness during the contract creation finalization step.
+
+	// GasChangeWitnessContractCreation flags a witness addition during the
+	// contract creation finalization step.
 	GasChangeWitnessContractCreation GasChangeReason = 16
-	// GasChangeWitnessCodeChunk flags the event of adding one or more contract code chunks to the witness.
+
+	// GasChangeWitnessCodeChunk flags adding one or more code chunks to the
+	// witness.
 	GasChangeWitnessCodeChunk GasChangeReason = 17
-	// GasChangeWitnessContractCollisionCheck flags the event of adding to the witness when checking for contract address collision.
+
+	// GasChangeWitnessContractCollisionCheck flags a witness addition during the
+	// contract address collision check.
 	GasChangeWitnessContractCollisionCheck GasChangeReason = 18
-	// GasChangeTxDataFloor is the amount of extra gas the transaction has to pay to reach the minimum gas requirement for the
-	// transaction data. This change will always be a negative change.
+
+	// GasChangeTxDataFloor is the extra gas charged to meet the EIP-7623
+	// calldata floor. Always a decrease.
 	GasChangeTxDataFloor GasChangeReason = 19
 
-	// GasChangeRefundAccountCreation represents the cancellation of a
-	// pre-charged account-creation cost when no account is created.
+	// GasChangeRefundAccountCreation cancels a pre-charged account-creation cost
+	// when no account is created.
 	GasChangeRefundAccountCreation GasChangeReason = 20
 
-	// GasChangeTxRuntimeGas is the amount of gas charged for the state-dependent
-	// costs of the transaction per EIP-2780.
+	// GasChangeTxRuntimeGas is the gas charged for the state-dependent costs of
+	// the transaction per EIP-2780.
 	GasChangeTxRuntimeGas GasChangeReason = 21
 
-	// GasChangeAccountCreation represents the conditional account-creation
-	// state cost charged in the creating frame when a CREATE/CREATE2 is about
-	// to create a new account (EIP-8037).
+	// GasChangeAccountCreation is the conditional account-creation state cost
+	// charged in the creating frame when a CREATE/CREATE2 is about to create a
+	// new account (EIP-8037).
 	GasChangeAccountCreation GasChangeReason = 22
 
-	// GasChangeIgnored is a special value that can be used to indicate that the gas change should be ignored as
-	// it will be "manually" tracked by a direct emit of the gas change event.
+	// GasChangeIgnored indicates the gas change should be ignored, as it is
+	// tracked manually by a direct emit of the gas change event.
 	GasChangeIgnored GasChangeReason = 0xFF
 )
 
@@ -513,11 +533,11 @@ const (
 	// NonceChangeAuthorization is the nonce change due to a EIP-7702 authorization.
 	NonceChangeAuthorization NonceChangeReason = 5
 
-	// NonceChangeRevert is emitted when the nonce is reverted back to a previous value due to call failure.
-	// It is only emitted when the tracer has opted in to use the journaling wrapper (WrapWithJournal).
+	// NonceChangeRevert reverts the nonce to a previous value on call failure.
+	// Emitted only when the tracer opts into WrapWithJournal.
 	NonceChangeRevert NonceChangeReason = 6
 
-	// NonceChangeSelfdestruct is emitted when the nonce is reset to zero due to a self-destruct
+	// NonceChangeSelfdestruct resets the nonce to zero on a self-destruct.
 	NonceChangeSelfdestruct NonceChangeReason = 7
 )
 
@@ -529,22 +549,25 @@ type CodeChangeReason byte
 const (
 	CodeChangeUnspecified CodeChangeReason = 0
 
-	// CodeChangeContractCreation is when a new contract is deployed via CREATE/CREATE2 operations.
+	// CodeChangeContractCreation is when a new contract is deployed via
+	// CREATE/CREATE2 operations.
 	CodeChangeContractCreation CodeChangeReason = 1
 
-	// CodeChangeGenesis is when contract code is set during blockchain genesis or initial setup.
+	// CodeChangeGenesis is when contract code is set during blockchain genesis
+	// or initial setup.
 	CodeChangeGenesis CodeChangeReason = 2
 
 	// CodeChangeAuthorization is when code is set via EIP-7702 Set Code Authorization.
 	CodeChangeAuthorization CodeChangeReason = 3
 
-	// CodeChangeAuthorizationClear is when EIP-7702 delegation is cleared by setting to zero address.
+	// CodeChangeAuthorizationClear is when EIP-7702 delegation is cleared by
+	// setting to zero address.
 	CodeChangeAuthorizationClear CodeChangeReason = 4
 
 	// CodeChangeSelfDestruct is when contract code is cleared due to self-destruct.
 	CodeChangeSelfDestruct CodeChangeReason = 5
 
-	// CodeChangeRevert is emitted when the code is reverted back to a previous value due to call failure.
-	// It is only emitted when the tracer has opted in to use the journaling wrapper (WrapWithJournal).
+	// CodeChangeRevert reverts the code to a previous value on call failure.
+	// Emitted only when the tracer opts into WrapWithJournal.
 	CodeChangeRevert CodeChangeReason = 6
 )
```
