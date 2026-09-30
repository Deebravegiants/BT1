# [?] Merge branch 'dev' of github.com:klaytn/klaytn into sc-concurrency-crash-fix

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-07-05
Source: https://github.com/kaiachain/kaia/commit/328d7f2d2e54ab6f6b8acb3cf695e04d10019024
Type: security-commit

## Details
Merge branch 'dev' of github.com:klaytn/klaytn into sc-concurrency-crash-fix

## Patch
### api/api_ethereum.go
```diff
@@ -29,8 +29,6 @@ import (
 
 	"github.com/klaytn/klaytn/rlp"
 
-	"github.com/klaytn/klaytn/accounts/abi"
-
 	"github.com/klaytn/klaytn/blockchain"
 	"github.com/klaytn/klaytn/blockchain/state"
 	"github.com/klaytn/klaytn/blockchain/types"
@@ -1543,6 +1541,7 @@ func EthDoCall(ctx context.Context, b Backend, args EthTransactionArgs, blockNrO
 	// but we check in advance here in order to keep StateTransition.TransactionDb method as unchanged as possible
 	// and to clarify error reason correctly to serve eth namespace APIs.
 	// This case is handled by EthDoEstimateGas function.
+
 	if msg.Gas() < intrinsicGas {
 		return nil, 0, 0, fmt.Errorf("%w: msg.gas %d, want %d", blockchain.ErrIntrinsicGas, msg.Gas(), intrinsicGas)
 	}
@@ -1578,7 +1577,7 @@ func EthDoEstimateGas(ctx context.Context, b Backend, args EthTransactionArgs, b
 	// Binary search the gas requirement, as it may be higher than the amount used
 	var (
 		lo  uint64 = params.TxGas - 1
-		hi  uint64
+		hi  uint64 = params.UpperGasLimit
 		cap uint64
 	)
 	// Use zero address if sender unspecified.
@@ -1698,46 +1697,6 @@ func EthDoEstimateGas(ctx context.Context, b Backend, args EthTransactionArgs, b
 	return hexutil.Uint64(hi), nil
 }
 
-// isReverted checks given error is vm.ErrExecutionReverted
-func isReverted(err error) bool {
-	if errors.Is(err, vm.ErrExecutionReverted) {
-		return true
-	}
-	return false
-}
-
-// newRevertError wraps data returned when EVM execution was reverted.
-// Make sure that data is returned when execution reverted situation.
-func newRevertError(data []byte) *revertError {
-	reason, errUnpack := abi.UnpackRevert(data)
-	err := errors.New("execution reverted")
-	if errUnpack == nil {
-		err = fmt.Errorf("execution reverted: %v", reason)
-	}
-	return &revertError{
-		error:  err,
-		reason: hexutil.Encode(data),
-	}
-}
-
-// revertError is an API error that encompassas an EVM revertal with JSON error
-// code and a binary data blob.
-type revertError struct {
-	error
-	reason string // revert reason hex encoded
-}
-
-// ErrorCode returns the JSON error code for a revertal.
-// See: https://github.com/ethereum/wiki/wiki/JSON-RPC-Error-Codes-Improvement-Proposal
-func (e *revertError) ErrorCode() int {
-	return 3
-}
-
-// ErrorData returns the hex encoded revert reason.
-func (e *revertError) ErrorData() interface{} {
-	return e.reason
-}
-
 // checkTxFee is an internal function used to check whether the fee of
 // the given transaction is _reasonable_(under the cap).
 func checkTxFee(gasPrice *big.Int, gas uint64, cap float64) error {
```

### api/api_public_blockchain.go
```diff
@@ -22,6 +22,7 @@ package api
 
 import (
 	"context"
+	"errors"
 	"fmt"
 	"math/big"
 	"time"
@@ -92,13 +93,13 @@ func (s *PublicBlockChainAPI) IsContractAccount(ctx context.Context, address com
 
 // IsHumanReadable returns true if the account associated with addr is a human-readable account.
 // It returns false otherwise.
-//func (s *PublicBlockChainAPI) IsHumanReadable(ctx context.Context, address common.Address, blockNr rpc.BlockNumber) (bool, error) {
+// func (s *PublicBlockChainAPI) IsHumanReadable(ctx context.Context, address common.Address, blockNr rpc.BlockNumber) (bool, error) {
 //	state, _, err := s.b.StateAndHeaderByNumber(ctx, blockNr)
 //	if err != nil {
 //		return false, err
 //	}
 //	return state.IsHumanReadable(address), state.Error()
-//}
+// }
 
 // GetBlockReceipts returns all the transaction receipts for the given block hash.
 func (s *PublicBlockChainAPI) GetBlockReceipts(ctx context.Context, blockHash common.Hash) ([]map[string]interface{}, error) {
@@ -255,52 +256,34 @@ func (s *PublicBlockChainAPI) IsSenderTxHashIndexingEnabled() bool {
 }
 
 // CallArgs represents the arguments for a call.
+// TODO-Klaytn: add KIP-71 related parameter
 type CallArgs struct {
 	From     common.Address  `json:"from"`
 	To       *common.Address `json:"to"`
 	Gas      hexutil.Uint64  `json:"gas"`
 	GasPrice hexutil.Big     `json:"gasPrice"`
 	Value    hexutil.Big     `json:"value"`
 	Data     hexutil.Bytes   `json:"data"`
+	Input    hexutil.Bytes   `json:"input"`
 }
 
-func DoCall(ctx context.Context, b Backend, args CallArgs, blockNrOrHash rpc.BlockNumberOrHash, vmCfg vm.Config, timeout time.Duration, globalGasCap *big.Int) ([]byte, uint64, uint64, bool, error) {
+func (args *CallArgs) data() []byte {
+	if args.Input != nil {
+		return args.Input
+	}
+	if args.Data != nil {
+		return args.Data
+	}
+	return nil
+}
+
+func DoCall(ctx context.Context, b Backend, args CallArgs, blockNrOrHash rpc.BlockNumberOrHash, vmCfg vm.Config, timeout time.Duration, globalGasCap *big.Int) ([]byte, uint64, uint64, uint, error) {
 	defer func(start time.Time) { logger.Debug("Executing EVM call finished", "runtime", time.Since(start)) }(time.Now())
 
 	state, header, err := b.StateAndHeaderByNumberOrHash(ctx, blockNrOrHash)
 	if state == nil || err != nil {
-		return nil, 0, 0, false, err
-	}
-	// Set sender address or use a default if none specified
-	addr := args.From
-	if addr == (common.Address{}) {
-		if wallets := b.AccountManager().Wallets(); len(wallets) > 0 {
-			if accounts := wallets[0].Accounts(); len(accounts) > 0 {
-				addr = accounts[0].Address
-			}
-		}
+		return nil, 0, 0, 0, err
 	}
-	// Set default gas & gas price if none were set
-	gas, gasPrice := uint64(args.Gas), args.GasPrice.ToInt()
-	if gas == 0 {
-		gas = math.MaxUint64 / 2
-	}
-	if globalGasCap != nil && globalGasCap.Uint64() < gas {
-		logger.Warn("Caller gas above allowance, capping", "requested", gas, "cap", globalGasCap)
-		gas = globalGasCap.Uint64()
-	}
-	if gasPrice.Sign() == 0 {
-		gasPrice = new(big.Int).SetUint64(defaultGasPrice)
-	}
-
-	intrinsicGas, err := types.IntrinsicGas(args.Data, nil, args.To == nil, b.ChainConfig().Rules(header.Number))
-	if err != nil {
-		return nil, 0, 0, false, err
-	}
-
-	// Create new call message
-	msg := types.NewMessage(addr, args.To, 0, args.Value.ToInt(), gas, gasPrice, args.Data, false, intrinsicGas)
-
 	// Setup context so it may be cancelled the call has completed
 	// or, in case of unmetered gas, setup a context with a timeout.
 	var cancel context.CancelFunc
@@ -313,12 +296,29 @@ func DoCall(ctx context.Context, b Backend, args CallArgs, blockNrOrHash rpc.Blo
 	// this makes sure resources are cleaned up.
 	defer cancel()
 
+	// TODO-Klaytn: Klaytn is using fixed baseFee as now but, if we change this fixed baseFee as dynamic baseFee, we should update this logic too.
+	fixedBaseFee := new(big.Int).SetUint64(params.BaseFee)
+	intrinsicGas, err := types.IntrinsicGas(args.data(), nil, args.To == nil, b.ChainConfig().Rules(header.Number))
+	if err != nil {
+		return nil, 0, 0, 0, err
+	}
+	msg, err := args.ToMessage(globalGasCap.Uint64(), fixedBaseFee, intrinsicGas)
 	// Add gas fee to sender for estimating gasLimit/computing cost or calling a function by insufficient balance sender.
 	state.AddBalance(msg.ValidatedSender(), new(big.Int).Mul(new(big.Int).SetUint64(msg.Gas()), msg.GasPrice()))
-	// Get a new instance of the EVM.
+
+	if err != nil {
+		return nil, 0, 0, 0, err
+	}
+	// The intrinsicGas is checked again later in the blockchain.ApplyMessage function,
+	// but we check in advance here in order to keep StateTransition.TransactionDb method as unchanged as possible
+	// and to clarify error reason correctly to serve eth namespace APIs.
+	// This case is handled by DoEstimateGas function.
+	if msg.Gas() < intrinsicGas {
+		return nil, 0, 0, 0, fmt.Errorf("%w: msg.gas %d, want %d", blockchain.ErrIntrinsicGas, msg.Gas(), intrinsicGas)
+	}
 	evm, vmError, err := b.GetEVM(ctx, msg, state, header, vmCfg)
 	if err != nil {
-		return nil, 0, 0, false, err
+		return nil, 0, 0, 0, err
 	}
 	// Wait for the context to be done and cancel the evm. Even if the
 	// EVM has finished, cancelling may be done (repeatedly)
@@ -327,39 +327,58 @@ func DoCall(ctx context.Context, b Backend, args CallArgs, blockNrOrHash rpc.Blo
 		evm.Cancel(vm.CancelByCtxDone)
 	}()
 
+	// Execute the message.
 	res, gas, kerr := blockchain.ApplyMessage(evm, msg)
 	err = kerr.ErrTxInvalid
 	if err := vmError(); err != nil {
-		return nil, 0, 0, false, err
+		return nil, 0, 0, 0, err
 	}
 	// If the timer caused an abort, return an appropriate error message
 	if evm.Cancelled() {
-		return nil, 0, 0, false, fmt.Errorf("execution aborted (timeout = %v)", timeout)
+		return nil, 0, 0, 0, fmt.Errorf("execution aborted (timeout = %v)", timeout)
 	}
-
-	// Propagate error of Receipt as JSON RPC error
-	if err == nil {
-		err = blockchain.GetVMerrFromReceiptStatus(kerr.Status)
+	if err != nil {
+		return res, 0, 0, 0, fmt.Errorf("err: %w (supplied gas %d)", err, msg.Gas())
 	}
-
-	return res, gas, evm.GetOpCodeComputationCost(), kerr.Status != types.ReceiptStatusSuccessful, err
+	// TODO-Klaytn-Interface: Introduce ExecutionResult struct from geth to return more detail information
+	return res, gas, evm.GetOpCodeComputationCost(), kerr.Status, nil
 }
 
 // Call executes the given transaction on the state for the given block number or hash.
 // It doesn't make and changes in the state/blockchain and is useful to execute and retrieve values.
 func (s *PublicBlockChainAPI) Call(ctx context.Context, args CallArgs, blockNrOrHash rpc.BlockNumberOrHash) (hexutil.Bytes, error) {
-	result, _, _, _, err := DoCall(ctx, s.b, args, blockNrOrHash, vm.Config{}, localTxExecutionTime, s.b.RPCGasCap())
-	return (hexutil.Bytes)(result), err
+	gasCap := big.NewInt(0)
+	if rpcGasCap := s.b.RPCGasCap(); rpcGasCap != nil {
+		gasCap = rpcGasCap
+	}
+	result, _, _, status, err := DoCall(ctx, s.b, args, blockNrOrHash, vm.Config{}, localTxExecutionTime, gasCap)
+	if err != nil {
+		return nil, err
+	}
+
+	err = blockchain.GetVMerrFromReceiptStatus(status)
+	if err != nil && isReverted(err) && len(result) > 0 {
+		return nil, newRevertError(result)
+	}
+	return common.CopyBytes(result), err
 }
 
 func (s *PublicBlockChainAPI) EstimateComputationCost(ctx context.Context, args CallArgs, blockNrOrHash rpc.BlockNumberOrHash) (hexutil.Uint64, error) {
-	_, _, computationCost, _, err := DoCall(ctx, s.b, args, blockNrOrHash, vm.Config{UseOpcodeComputationCost: true}, localTxExecutionTime, s.b.RPCGasCap())
+	gasCap := big.NewInt(0)
+	if rpcGasCap := s.b.RPCGasCap(); rpcGasCap != nil {
+		gasCap = rpcGasCap
+	}
+	_, _, computationCost, _, err := DoCall(ctx, s.b, args, blockNrOrHash, vm.Config{UseOpcodeComputationCost: true}, localTxExecutionTime, gasCap)
 	return (hexutil.Uint64)(computationCost), err
 }
 
 // EstimateGas returns an estimate of the amount of gas needed to execute the given transaction against the latest block.
 func (s *PublicBlockChainAPI) EstimateGas(ctx context.Context, args CallArgs) (hexutil.Uint64, error) {
-	return s.DoEstimateGas(ctx, s.b, args, s.b.RPCGasCap())
+	gasCap := uint64(0)
+	if rpcGasCap := s.b.RPCGasCap(); rpcGasCap != nil {
+		gasCap = rpcGasCap.Uint64()
+	}
+	return s.DoEstimateGas(ctx, s.b, args, big.NewInt(int64(gasCap)))
 }
 
 func (s *PublicBlockChainAPI) DoEstimateGas(ctx context.Context, b Backend, args CallArgs, gasCap *big.Int) (hexutil.Uint64, error) {
@@ -375,35 +394,57 @@ func (s *PublicBlockChainAPI) DoEstimateGas(ctx context.Context, b Backend, args
 		// Retrieve the current pending block to act as the gas ceiling
 		hi = params.UpperGasLimit
 	}
-	if gasCap != nil && hi > gasCap.Uint64() {
-		logger.Warn("Caller gas above allowance, capping", "requested", hi, "cap", gasCap)
-		hi = gasCap.Uint64()
-	}
+	// TODO-Klaytn: set hi value with account balance
 	cap = hi
 
 	// Create a helper to check if a gas allowance results in an executable transaction
-	executable := func(gas uint64) bool {
+	executable := func(gas uint64) (bool, []byte, error, error) {
 		args.Gas = hexutil.Uint64(gas)
-
-		_, _, _, failed, err := DoCall(ctx, b, args, rpc.NewBlockNumberOrHashWithNumber(rpc.LatestBlockNumber), vm.Config{UseOpcodeComputationCost: true}, localTxExecutionTime, gasCap)
-		if err != nil || failed {
-			return false
+		ret, _, _, status, err := DoCall(ctx, b, args, rpc.NewBlockNumberOrHashWithNumber(rpc.LatestBlockNumber), vm.Config{}, 0, gasCap)
+		if err != nil {
+			if errors.Is(err, blockchain.ErrIntrinsicGas) {
+				// Special case, raise gas limit
+				return false, ret, nil, nil
+			}
+			// Returns error when it is not VM error (less balance or wrong nonce, etc...).
+			return false, nil, nil, err
+		}
+		// If err is vmError, return vmError with returned data
+		vmErr := blockchain.GetVMerrFromReceiptStatus(status)
+		if vmErr != nil {
+			return false, ret, vmErr, nil
 		}
-		return true
+		return true, ret, vmErr, nil
 	}
 	// Execute the binary search and hone in on an executable gas limit
 	for lo+1 < hi {
 		mid := (hi + lo) / 2
-		if !executable(mid) {
+		isExecutable, _, _, err := executable(mid)
+		if err != nil {
+			return 0, err
+		}
+		if !isExecutable {
 			lo = mid
 		} else {
 			hi = mid
 		}
 	}
 	// Reject the transaction as invalid if it still fails at the highest allowance
 	if hi == cap {
-		if !executable(hi) {
-			return 0, fmt.Errorf("gas required exceeds allowance or always failing transaction")
+		isExecutable, ret, vmErr, err := executable(hi)
+		if err != nil {
+			return 0, err
+		}
+		if !isExecutable {
+			if vmErr != nil {
+				// Treat vmErr as RevertError only when there was returned data from call.
+				if isReverted(vmErr) && len(ret) > 0 {
+					return 0, newRevertError(ret)
+				}
+				return 0, vmErr
+			}
+			// Otherwise, the specified gas cap is too low
+			return 0, fmt.Errorf("gas required exceeds allowance (%d)", cap)
 		}
 	}
 	return hexutil.Uint64(hi), nil
@@ -606,3 +647,62 @@ func newRPCTransactionFromBlockHash(b *types.Block, hash common.Hash) map[string
 	}
 	return nil
 }
+
+func (args *CallArgs) ToMessage(globalGasCap uint64, baseFee *big.Int, intrinsicGas uint64) (*types.Transaction, error) {
+	// Set sender address or use zero address if none specified.
+	addr := args.From
+
+	// Set default gas & gas price if none were set
+	gas := globalGasCap
+	if gas == 0 {
+		gas = uint64(math.MaxUint64 / 2)
+	}
+	if args.Gas != 0 {
+		gas = uint64(args.Gas)
+	}
+	if globalGasCap != 0 && globalGasCap < gas {
+		logger.Warn("Caller gas above allowance, capping", "requested", gas, "cap", globalGasCap)
+		gas = globalGasCap
+	}
+
+	var (
+		gasPrice  *big.Int
+		gasFeeCap *big.Int
+		gasTipCap *big.Int
+	)
+	if baseFee == nil {
+		// If there's no basefee, then it must be a non-1559 execution
+		gasPrice = new(big.Int)
+		if &args.GasPrice != nil {
+			gasPrice = args.GasPrice.ToInt()
+		}
+		gasFeeCap, gasTipCap = gasPrice, gasPrice
+	} else {
+		// A basefee is provided, necessitating 1559-type execution
+		if &args.GasPrice != nil {
+			// User specified the legacy gas field, convert to 1559 gas typing
+			gasPrice = args.GasPrice.ToInt()
+			gasFeeCap, gasTipCap = gasPrice, gasPrice
+		} else {
+			// TODO-Klaytn: User specified 1559 gas fields (or none), use those
+			gasFeeCap = new(big.Int)
+			gasTipCap = new(big.Int)
+			// Backfill the legacy gasPrice for EVM execution, unless we're all zeros
+			gasPrice = new(big.Int)
+			if gasFeeCap.BitLen() > 0 || gasTipCap.BitLen() > 0 {
+				gasPrice = math.BigMin(new(big.Int).Add(gasTipCap, baseFee), gasFeeCap)
+			}
+		}
+	}
+	value := new(big.Int)
+	if &args.Value != nil {
+		value = args.Value.ToInt()
+	}
+
+	// TODO-Klaytn: Klaytn does not support accessList yet.
+	// var accessList types.AccessList
+	// if args.AccessList != nil {
+	//	 accessList = *args.AccessList
+	// }
+	return types.NewMessage(addr, args.To, 0, value, gas, gasPrice, args.data(), false, intrinsicGas), nil
+}
```

### api/tx_args.go
```diff
@@ -28,8 +28,10 @@ import (
 	"math/big"
 	"reflect"
 
+	"github.com/klaytn/klaytn/accounts/abi"
 	"github.com/klaytn/klaytn/blockchain/types"
 	"github.com/klaytn/klaytn/blockchain/types/accountkey"
+	"github.com/klaytn/klaytn/blockchain/vm"
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/common/hexutil"
 	"github.com/klaytn/klaytn/params"
@@ -445,3 +447,43 @@ func (args *AccountUpdateTxArgs) toTransaction() (*types.Transaction, error) {
 
 	return tx, nil
 }
+
+// isReverted checks given error is vm.ErrExecutionReverted
+func isReverted(err error) bool {
+	if errors.Is(err, vm.ErrExecutionReverted) {
+		return true
+	}
+	return false
+}
+
+// newRevertError wraps data returned when EVM execution was reverted.
+// Make sure that data is returned when execution reverted situation.
+func newRevertError(data []byte) *revertError {
+	reason, errUnpack := abi.UnpackRevert(data)
+	err := errors.New("execution reverted")
+	if errUnpack == nil {
+		err = fmt.Errorf("execution reverted: %v", reason)
+	}
+	return &revertError{
+		error:  err,
+		reason: hexutil.Encode(data),
+	}
+}
+
+// revertError is an API error that encompassas an EVM revertal with JSON error
+// code and a binary data blob.
+type revertError struct {
+	error
+	reason string // revert reason hex encoded
+}
+
+// ErrorCode returns the JSON error code for a revertal.
+// See: https://github.com/ethereum/wiki/wiki/JSON-RPC-Error-Codes-Improvement-Proposal
+func (e *revertError) ErrorCode() int {
+	return 3
+}
+
+// ErrorData returns the hex encoded revert reason.
+func (e *revertError) ErrorData() interface{} {
+	return e.reason
+}
```

### blockchain/state/sync_test.go
```diff
@@ -27,8 +27,10 @@ import (
 
 	"github.com/alecthomas/units"
 	lru "github.com/hashicorp/golang-lru"
+	"github.com/klaytn/klaytn/blockchain/types/account"
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/crypto"
+	"github.com/klaytn/klaytn/rlp"
 	"github.com/klaytn/klaytn/storage/database"
 	"github.com/klaytn/klaytn/storage/statedb"
 	"github.com/stretchr/testify/assert"
@@ -180,59 +182,97 @@ func TestEmptyStateSync(t *testing.T) {
 
 	// only bloom
 	{
-		bloom := statedb.NewSyncBloom(1, database.NewMemDB())
-		if req := NewStateSync(empty, database.NewMemoryDBManager(), bloom, nil).Missing(1); len(req) != 0 {
-			t.Errorf("content requested for empty state: %v", req)
+		db := database.NewMemoryDBManager()
+		sync := NewStateSync(empty, db, statedb.NewSyncBloom(1, db.GetMemDB()), nil)
+		if nodes, paths, codes := sync.Missing(1); len(nodes) != 0 || len(paths) != 0 || len(codes) != 0 {
+			t.Errorf("content requested for empty state: %v", sync)
 		}
 	}
 
 	// only lru
 	{
 		lruCache, _ := lru.New(int(1 * units.MB / common.HashLength))
-		if req := NewStateSync(empty, database.NewMemoryDBManager(), nil, lruCache).Missing(1); len(req) != 0 {
-			t.Errorf("content requested for empty state: %v", req)
+		db := database.NewMemoryDBManager()
+		sync := NewStateSync(empty, db, statedb.NewSyncBloom(1, db.GetMemDB()), lruCache)
+		if nodes, paths, codes := sync.Missing(1); len(nodes) != 0 || len(paths) != 0 || len(codes) != 0 {
+			t.Errorf("content requested for empty state: %v", sync)
 		}
 	}
 
 	// no bloom lru
 	{
-		if req := NewStateSync(empty, database.NewMemoryDBManager(), nil, nil).Missing(1); len(req) != 0 {
-			t.Errorf("content requested for empty state: %v", req)
+		db := database.NewMemoryDBManager()
+		sync := NewStateSync(empty, db, nil, nil)
+		if nodes, paths, codes := sync.Missing(1); len(nodes) != 0 || len(paths) != 0 || len(codes) != 0 {
+			t.Errorf("content requested for empty state: %v", sync)
 		}
 	}
 
 	// both bloom, lru
 	{
 		bloom := statedb.NewSyncBloom(1, database.NewMemDB())
 		lruCache, _ := lru.New(int(1 * units.MB / common.HashLength))
-		if req := NewStateSync(empty, database.NewMemoryDBManager(), bloom, lruCache).Missing(1); len(req) != 0 {
-			t.Errorf("content requested for empty state: %v", req)
+		db := database.NewMemoryDBManager()
+		sync := NewStateSync(empty, db, bloom, lruCache)
+		if nodes, paths, codes := sync.Missing(1); len(nodes) != 0 || len(paths) != 0 || len(codes) != 0 {
+			t.Errorf("content requested for empty state: %v", sync)
 		}
 	}
 }
 
 // Tests that given a root hash, a state can sync iteratively on a single thread,
 // requesting retrieval tasks and returning all of them in one go.
-func TestIterativeStateSyncIndividual(t *testing.T)         { testIterativeStateSync(t, 1, false) }
-func TestIterativeStateSyncBatched(t *testing.T)            { testIterativeStateSync(t, 100, false) }
-func TestIterativeStateSyncIndividualFromDisk(t *testing.T) { testIterativeStateSync(t, 1, true) }
-func TestIterativeStateSyncBatchedFromDisk(t *testing.T)    { testIterativeStateSync(t, 100, true) }
+func TestIterativeStateSyncIndividual(t *testing.T) {
+	testIterativeStateSync(t, 1, false, false)
+}
+
+func TestIterativeStateSyncBatched(t *testing.T) {
+	testIterativeStateSync(t, 100, false, false)
+}
+
+func TestIterativeStateSyncIndividualFromDisk(t *testing.T) {
+	testIterativeStateSync(t, 1, true, false)
+}
+
+func TestIterativeStateSyncBatchedFromDisk(t *testing.T) {
+	testIterativeStateSync(t, 100, true, false)
+}
+
+func TestIterativeStateSyncIndividualByPath(t *testing.T) {
+	testIterativeStateSync(t, 1, false, true)
+}
 
-func testIterativeStateSync(t *testing.T, count int, commit bool) {
+func TestIterativeStateSyncBatchedByPath(t *testing.T) {
+	testIterativeStateSync(t, 100, false, true)
+}
+
+func testIterativeStateSync(t *testing.T, count int, commit bool, bypath bool) {
 	// Create a random state to copy
 	srcState, srcRoot, srcAccounts := makeTestState(t)
 	if commit {
 		srcState.TrieDB().Commit(srcRoot, false, 0)
 	}
+	srcTrie, _ := statedb.NewTrie(srcRoot, srcState.TrieDB())
+
 	// Create a destination state and sync with the scheduler
 	dstDiskDb := database.NewMemoryDBManager()
 	dstState := NewDatabase(dstDiskDb)
 	sched := NewStateSync(srcRoot, dstDiskDb, statedb.NewSyncBloom(1, dstDiskDb.GetMemDB()), nil)
 
-	queue := append([]common.Hash{}, sched.Missing(count)...)
-	for len(queue) > 0 {
-		results := make([]statedb.SyncResult, len(queue))
-		for i, hash := range queue {
+	nodes, paths, codes := sched.Missing(count)
+	var (
+		hashQueue []common.Hash
+		pathQueue []statedb.SyncPath
+	)
+	if !bypath {
+		hashQueue = append(append(hashQueue[:0], nodes...), codes...)
+	} else {
+		hashQueue = append(hashQueue[:0], codes...)
+		pathQueue = append(pathQueue[:0], paths...)
+	}
+	for len(hashQueue)+len(pathQueue) > 0 {
+		results := make([]statedb.SyncResult, len(hashQueue)+len(pathQueue))
+		for i, hash := range hashQueue {
 			data, err := srcState.TrieDB().Node(hash)
 			if err != nil {
 				data, err = srcState.ContractCode(hash)
@@ -242,6 +282,34 @@ func testIterativeStateSync(t *testing.T, count int, commit bool) {
 			}
 			results[i] = statedb.SyncResult{Hash: hash, Data: data}
 		}
+		for i, path := range pathQueue {
+			if len(path) == 1 {
+				data, _, err := srcTrie.TryGetNode(path[0])
+				if err != nil {
+					t.Fatalf("failed to retrieve node data for path %x: %v", path, err)
+				}
+				results[len(hashQueue)+i] = statedb.SyncResult{Hash: crypto.Keccak256Hash(data), Data: data}
+			} else {
+				serializer := account.NewAccountSerializer()
+				if err := rlp.DecodeBytes(srcTrie.Get(path[0]), serializer); err != nil {
+					t.Fatalf("failed to decode account on path %x: %v", path, err)
+				}
+				acc := serializer.GetAccount()
+				pacc := account.GetProgramAccount(acc)
+				if pacc == nil {
+					t.Errorf("failed to get contract")
+				}
+				stTrie, err := statedb.NewTrie(pacc.GetStorageRoot(), srcState.TrieDB())
+				if err != nil {
+					t.Fatalf("failed to retriev storage trie for path %x: %v", path, err)
+				}
+				data, _, err := stTrie.TryGetNode(path[1])
+				if err != nil {
+					t.Fatalf("failed to retrieve node data for path %x: %v", path, err)
+				}
+				results[len(hashQueue)+i] = statedb.SyncResult{Hash: crypto.Keccak256Hash(data), Data: data}
+			}
+		}
 		for index, result := range results {
 			if err := sched.Process(result); err != nil {
 				t.Fatalf("failed to process result #%d: %v", index, err)
@@ -252,7 +320,14 @@ func testIterativeStateSync(t *testing.T, count int, commit bool) {
 			t.Fatalf("failed to commit data: %v", err)
 		}
 		batch.Write()
-		queue = append(queue[:0], sched.Missing(count)...)
+
+		nodes, paths, codes = sched.Missing(count)
+		if !bypath {
+			hashQueue = append(append(hashQueue[:0], nodes...), codes...)
+		} else {
+			hashQueue = append(hashQueue[:0], codes...)
+			pathQueue = append(pathQueue[:0], paths...)
+		}
 	}
 	// Cross check that the two states are in sync
 	checkStateAccounts(t, dstDiskDb, srcRoot, srcAccounts)
@@ -349,7 +424,9 @@ func TestIterativeDelayedStateSync(t *testing.T) {
 	dstState := NewDatabase(dstDiskDB)
 	sched := NewStateSync(srcRoot, dstDiskDB, statedb.NewSyncBloom(1, dstDiskDB.GetMemDB()), nil)
 
-	queue := append([]common.Hash{}, sched.Missing(0)...)
+	nodes, _, codes := sched.Missing(0)
+	queue := append(append([]common.Hash{}, nodes...), codes...)
+
 	for len(queue) > 0 {
 		// Sync only half of the scheduled nodes
 		results := make([]statedb.SyncResult, len(queue)/2+1)
@@ -373,7 +450,8 @@ func TestIterativeDelayedStateSync(t *testing.T) {
 			t.Fatalf("failed to commit data: %v", err)
 		}
 		batch.Write()
-		queue = append(queue[len(results):], sched.Missing(0)...)
+		nodes, _, codes := sched.Missing(0)
+		queue = append(append(queue[len(results):], nodes...), codes...)
 	}
 	// Cross check that the two states are in sync
 	checkStateAccounts(t, dstDiskDB, srcRoot, srcAccounts)
@@ -402,7 +480,8 @@ func testIterativeRandomStateSync(t *testing.T, count int) {
 	sched := NewStateSync(srcRoot, dstDb, statedb.NewSyncBloom(1, dstDb.GetMemDB()), nil)
 
 	queue := make(map[common.Hash]struct{})
-	for _, hash := range sched.Missing(count) {
+	nodes, _, codes := sched.Missing(count)
+	for _, hash := range append(nodes, codes...) {
 		queue[hash] = struct{}{}
 	}
 	for len(queue) > 0 {
@@ -430,7 +509,8 @@ func testIterativeRandomStateSync(t *testing.T, count int) {
 		}
 		batch.Write()
 		queue = make(map[common.Hash]struct{})
-		for _, hash := range sched.Missing(count) {
+		nodes, _, codes := sched.Missing(0)
+		for _, hash := range append(nodes, codes...) {
 			queue[hash] = struct{}{}
 		}
 	}
@@ -457,7 +537,8 @@ func TestIterativeRandomDelayedStateSync(t *testing.T) {
 	sched := NewStateSync(srcRoot, dstDb, statedb.NewSyncBloom(1, dstDb.GetMemDB()), nil)
 
 	queue := make(map[common.Hash]struct{})
-	for _, hash := range sched.Missing(0) {
+	nodes, _, codes := sched.Missing(0)
+	for _, hash := range append(nodes, codes...) {
 		queue[hash] = struct{}{}
 	}
 	for len(queue) > 0 {
@@ -490,7 +571,11 @@ func TestIterativeRandomDelayedStateSync(t *testing.T) {
 			t.Fatalf("failed to commit data: %v", err)
 		}
 		batch.Write()
-		for _, hash := range sched.Missing(0) {
+		for _, result := range results {
+			delete(queue, result.Hash)
+		}
+		nodes, _, codes = sched.Missing(0)
+		for _, hash := range append(nodes, codes...) {
 			queue[hash] = struct{}{}
 		}
 	}
@@ -528,7 +613,10 @@ func TestIncompleteStateSync(t *testing.T) {
 	sched := NewStateSync(srcRoot, dstDb, statedb.NewSyncBloom(1, dstDb.GetMemDB()), nil)
 
 	var added []common.Hash
-	queue := append([]common.Hash{}, sched.Missing(1)...)
+
+	nodes, _, codes := sched.Missing(1)
+	queue := append(append([]common.Hash{}, nodes...), codes...)
+
 	for len(queue) > 0 {
 		// Fetch a batch of state nodes
 		results := make([]statedb.SyncResult, len(queue))
@@ -568,7 +656,8 @@ func TestIncompleteStateSync(t *testing.T) {
 			}
 		}
 		// Fetch the next batch to retrieve
-		queue = append(queue[:0], sched.Missing(1)...)
+		nodes, _, codes = sched.Missing(1)
+		queue = append(append(queue[:0], nodes...), codes...)
 	}
 	// Sanity check that removing any node from the database is detected
 	for _, node := range added[1:] {
```

### blockchain/state_migration.go
```diff
@@ -151,7 +151,8 @@ func (bc *BlockChain) migrateState(rootHash common.Hash) (returnErr error) {
 
 	// Migration main loop
 	for trieSync.Pending() > 0 {
-		queue = append(queue[:0], trieSync.Missing(1024)...)
+		nodes, _, codes := trieSync.Missing(1024)
+		queue = append(queue[:0], append(nodes, codes...)...)
 		results := make([]statedb.SyncResult, len(queue))
 
 		// Read the trie nodes
```

### blockchain/tx_pool.go
```diff
@@ -295,11 +295,11 @@ func (pool *TxPool) loop() {
 				head = ev.Block
 				pool.mu.Unlock()
 			}
-			// Be unsubscribed due to system stopped
+		// Be unsubscribed due to system stopped
 		case <-pool.chainHeadSub.Err():
 			return
 
-			// Handle stats reporting ticks
+		// Handle stats reporting ticks
 		case <-report.C:
 			pool.mu.RLock()
 			pending, queued := pool.stats()
@@ -313,7 +313,7 @@ func (pool *TxPool) loop() {
 				txPoolQueueGauge.Update(int64(queued))
 			}
 
-			// Handle inactive account transaction eviction
+		// Handle inactive account transaction eviction
 		case <-evict.C:
 			pool.mu.Lock()
 			for addr, beat := range pool.beats {
@@ -335,7 +335,7 @@ func (pool *TxPool) loop() {
 			}
 			pool.mu.Unlock()
 
-			// Handle local transaction journal rotation
+		// Handle local transaction journal rotation
 		case <-journal.C:
 			if pool.journal != nil {
 				pool.mu.Lock()
@@ -378,33 +378,51 @@ func (pool *TxPool) reset(oldHead, newHead *types.Header) {
 				rem = pool.chain.GetBlock(oldHead.Hash(), oldHead.Number.Uint64())
 				add = pool.chain.GetBlock(newHead.Hash(), newHead.Number.Uint64())
 			)
-			for rem.NumberU64() > add.NumberU64() {
-				discarded = append(discarded, rem.Transactions()...)
-				if rem = pool.chain.GetBlock(rem.ParentHash(), rem.NumberU64()-1); rem == nil {
-					logger.Error("Unrooted old chain seen by tx pool", "block", oldHead.Number, "hash", oldHead.Hash())
+			if rem == nil {
+				// This can happen if a setHead function is performed.
+				// In this case we can simply discard the old head from the chain, and replace with newhead.
+
+				// If newNum >= oldNum, then it's not a case of setHead.
+				if newNum >= oldNum {
+					logger.Error("Transaction pool reset with missing oldhead",
+						"old", oldHead.Hash(), "oldnum", oldNum, "new", newHead.Hash(), "newnum", newNum)
 					return
+				} else {
+					// When setHead is performed, then oldHead becomes bigger than newHead, since newHead becomes rewinded blockNumber.
+					// If that is the case, we don't have the lost transactions anymore, and
+					// there's nothing to add
+					logger.Warn("Skipping transaction reset caused by setHead",
+						"old", oldHead.Hash(), "oldnum", oldNum, "new", newHead.Hash(), "newnum", newNum)
 				}
-			}
-			for add.NumberU64() > rem.NumberU64() {
-				included = append(included, add.Transactions()...)
-				if add = pool.chain.GetBlock(add.ParentHash(), add.NumberU64()-1); add == nil {
-					logger.Error("Unrooted new chain seen by tx pool", "block", newHead.Number, "hash", newHead.Hash())
-					return
+			} else {
+				for rem.NumberU64() > add.NumberU64() {
+					discarded = append(discarded, rem.Transactions()...)
+					if rem = pool.chain.GetBlock(rem.ParentHash(), rem.NumberU64()-1); rem == nil {
+						logger.Error("Unrooted old chain seen by tx pool", "block", oldHead.Number, "hash", oldHead.Hash())
+						return
+					}
 				}
-			}
-			for rem.Hash() != add.Hash() {
-				discarded = append(discarded, rem.Transactions()...)
-				if rem = pool.chain.GetBlock(rem.ParentHash(), rem.NumberU64()-1); rem == nil {
-					logger.Error("Unrooted old chain seen by tx pool", "block", oldHead.Number, "hash", oldHead.Hash())
-					return
+				for add.NumberU64() > rem.NumberU64() {
+					included = append(included, add.Transactions()...)
+					if add = pool.chain.GetBlock(add.ParentHash(), add.NumberU64()-1); add == nil {
+						logger.Error("Unrooted new chain seen by tx pool", "block", newHead.Number, "hash", newHead.Hash())
+						return
+					}
 				}
-				included = append(included, add.Transactions()...)
-				if add = pool.chain.GetBlock(add.ParentHash(), add.NumberU64()-1); add == nil {
-					logger.Error("Unrooted new chain seen by tx pool", "block", newHead.Number, "hash", newHead.Hash())
-					return
+				for rem.Hash() != add.Hash() {
+					discarded = append(discarded, rem.Transactions()...)
+					if rem = pool.chain.GetBlock(rem.ParentHash(), rem.NumberU64()-1); rem == nil {
+						logger.Error("Unrooted old chain seen by tx pool", "block", oldHead.Number, "hash", oldHead.Hash())
+						return
+					}
+					included = append(included, add.Transactions()...)
+					if add = pool.chain.GetBlock(add.ParentHash(), add.NumberU64()-1); add == nil {
+						logger.Error("Unrooted new chain seen by tx pool", "block", newHead.Number, "hash", newHead.Hash())
+						return
+					}
 				}
+				reinject = types.TxDifference(discarded, included)
 			}
-			reinject = types.TxDifference(discarded, included)
 		}
 	}
 	// Initialize the internal state to the current head
```

### consensus/istanbul/backend/api.go
```diff
@@ -54,7 +54,7 @@ func (api *API) GetSnapshot(number *rpc.BlockNumber) (*Snapshot, error) {
 	if header == nil {
 		return nil, errUnknownBlock
 	}
-	return api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil)
+	return api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil, false)
 }
 
 // GetSnapshotAtHash retrieves the state snapshot at a given block.
@@ -63,7 +63,7 @@ func (api *API) GetSnapshotAtHash(hash common.Hash) (*Snapshot, error) {
 	if header == nil {
 		return nil, errUnknownBlock
 	}
-	return api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil)
+	return api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil, false)
 }
 
 // GetValidators retrieves the list of authorized validators with the given block number.
@@ -178,7 +178,7 @@ func (api *APIExtension) GetCouncil(number *rpc.BlockNumber) ([]common.Address,
 	//}
 
 	// Calculate council list from snapshot
-	snap, err := api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil)
+	snap, err := api.istanbul.snapshot(api.chain, header.Number.Uint64(), header.Hash(), nil, false)
 	if err != nil {
 		logger.Error("Failed to get snapshot.", "hash", header.Hash(), "err", err)
 		return nil, errInternalError
@@ -236,7 +236,7 @@ func (api *APIExtension) GetCommittee(number *rpc.BlockNumber) ([]common.Address
 
 	// get the snapshot of the previous block.
 	parentHash := header.ParentHash
-	snap, err := api.istanbul.snapshot(api.chain, blockNumber-1, parentHash, nil)
+	snap, err := api.istanbul.snapshot(api.chain, blockNumber-1, parentHash, nil, false)
 	if err != nil {
 		return nil, err
 	}
@@ -287,7 +287,7 @@ func (api *APIExtension) getConsensusInfo(block *types.Block) (ConsensusInfo, er
 
 	// get the snapshot of the previous block.
 	parentHash := block.ParentHash()
-	snap, err := api.istanbul.snapshot(api.chain, blockNumber-1, parentHash, nil)
+	snap, err := api.istanbul.snapshot(api.chain, blockNumber-1, parentHash, nil, false)
 	if err != nil {
 		return ConsensusInfo{}, err
 	}
```

### consensus/istanbul/backend/backend.go
```diff
@@ -392,7 +392,7 @@ func (sb *backend) ParentValidators(proposal istanbul.Proposal) istanbul.Validat
 }
 
 func (sb *backend) getValidators(number uint64, hash common.Hash) istanbul.ValidatorSet {
-	snap, err := sb.snapshot(sb.chain, number, hash, nil)
+	snap, err := sb.snapshot(sb.chain, number, hash, nil, true)
 	if err != nil {
 		logger.Error("Snapshot not found.", "err", err)
 		// TODO-Klaytn-Governance The following return case should not be called. Refactor it to error handling.
```

### consensus/istanbul/backend/engine.go
```diff
@@ -264,7 +264,7 @@ func (sb *backend) verifySigner(chain consensus.ChainReader, header *types.Heade
 	}
 
 	// Retrieve the snapshot needed to verify this header and cache it
-	snap, err := sb.snapshot(chain, number-1, header.ParentHash, parents)
+	snap, err := sb.snapshot(chain, number-1, header.ParentHash, parents, true)
 	if err != nil {
 		return err
 	}
@@ -291,7 +291,7 @@ func (sb *backend) verifyCommittedSeals(chain consensus.ChainReader, header *typ
 	}
 
 	// Retrieve the snapshot needed to verify this header and cache it
-	snap, err := sb.snapshot(chain, number-1, header.ParentHash, parents)
+	snap, err := sb.snapshot(chain, number-1, header.ParentHash, parents, true)
 	if err != nil {
 		return err
 	}
@@ -365,7 +365,7 @@ func (sb *backend) Prepare(chain consensus.ChainReader, header *types.Header) er
 	header.BlockScore = defaultBlockScore
 
 	// Assemble the voting snapshot
-	snap, err := sb.snapshot(chain, number-1, header.ParentHash, nil)
+	snap, err := sb.snapshot(chain, number-1, header.ParentHash, nil, true)
 	if err != nil {
 		return err
 	}
@@ -466,7 +466,7 @@ func (sb *backend) Seal(chain consensus.ChainReader, block *types.Block, stop <-
 	number := header.Number.Uint64()
 
 	// Bail out if we're unauthorized to sign a block
-	snap, err := sb.snapshot(chain, number-1, header.ParentHash, nil)
+	snap, err := sb.snapshot(chain, number-1, header.ParentHash, nil, true)
 	if err != nil {
 		return nil, err
 	}
@@ -657,12 +657,12 @@ func getPrevHeaderAndUpdateParents(chain consensus.ChainReader, number uint64, h
 
 // CreateSnapshot does not return a snapshot but creates a new snapshot at a given point in time.
 func (sb *backend) CreateSnapshot(chain consensus.ChainReader, number uint64, hash common.Hash, parents []*types.Header) error {
-	_, err := sb.snapshot(chain, number, hash, parents)
+	_, err := sb.snapshot(chain, number, hash, parents, true)
 	return err
 }
 
 // snapshot retrieves the authorization snapshot at a given point in time.
-func (sb *backend) snapshot(chain consensus.ChainReader, number uint64, hash common.Hash, parents []*types.Header) (*Snapshot, error) {
+func (sb *backend) snapshot(chain consensus.ChainReader, number uint64, hash common.Hash, parents []*types.Header, writable bool) (*Snapshot, error) {
 	// Search for a snapshot in memory or on disk for checkpoints
 	var (
 		headers []*types.Header
@@ -703,13 +703,13 @@ func (sb *backend) snapshot(chain consensus.ChainReader, number uint64, hash com
 	for i := 0; i < len(headers)/2; i++ {
 		headers[i], headers[len(headers)-1-i] = headers[len(headers)-1-i], headers[i]
 	}
-	snap, err := snap.apply(headers, sb.governance, sb.address, sb.governance.ProposerPolicy(), chain)
+	snap, err := snap.apply(headers, sb.governance, sb.address, sb.governance.ProposerPolicy(), chain, writable)
 	if err != nil {
 		return nil, err
 	}
 
 	// If we've generated a new checkpoint snapshot, save to disk
-	if snap.Number%checkpointInterval == 0 && len(headers) > 0 {
+	if writable && snap.Number%checkpointInterval == 0 && len(headers) > 0 {
 		if sb.governance.CanWriteGovernanceState(snap.Number) {
 			sb.governance.WriteGovernanceState(snap.Number, true)
 		}
```

### consensus/istanbul/backend/engine_test.go
```diff
@@ -823,7 +823,7 @@ func TestSnapshot_Validators_AfterMinimumStakingVotes(t *testing.T) {
 		for _, e := range tc.expected {
 			for _, num := range e.blocks {
 				block := chain.GetBlockByNumber(num)
-				snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil)
+				snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil, true)
 				assert.NoError(t, err)
 
 				validators := toAddressList(snap.ValSet.List())
@@ -994,7 +994,7 @@ func TestSnapshot_Validators_BasedOnStaking(t *testing.T) {
 		_, err := chain.InsertChain(types.Blocks{block})
 		assert.NoError(t, err)
 
-		snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil)
+		snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil, true)
 		assert.NoError(t, err)
 
 		validators := toAddressList(snap.ValSet.List())
@@ -1215,7 +1215,7 @@ func TestSnapshot_Validators_AddRemove(t *testing.T) {
 				continue
 			}
 			block := chain.GetBlockByNumber(uint64(i))
-			snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil)
+			snap, err := engine.snapshot(chain, block.NumberU64(), block.Hash(), nil, true)
 			assert.NoError(t, err)
 			validators := copyAndSortAddrs(toAddressList(snap.ValSet.List()))
 
@@ -1229,6 +1229,52 @@ func TestSnapshot_Validators_AddRemove(t *testing.T) {
 	}
 }
 
+func TestSnapshot_Writable(t *testing.T) {
+	var configItems []interface{}
+	configItems = append(configItems, proposerPolicy(params.WeightedRandom))
+	configItems = append(configItems, epoch(3))
+	configItems = append(configItems, governanceMode("single"))
+	configItems = append(configItems, blockPeriod(0)) // set block period to 0 to prevent creating future block
+	chain, engine := newBlockChain(1, configItems...)
+
+	// add votes and insert voted blocks
+	var (
+		previousBlock, currentBlock *types.Block = nil, chain.Genesis()
+		err                         error
+	)
+
+	// voteData is inserted at block 4, and current block is block 5.
+	for i := 0; i < 5; i++ {
+		if i == 4 {
+			engine.governance.AddVote("governance.unitprice", uint64(2000000))
+		}
+		previousBlock = currentBlock
+		currentBlock = makeBlockWithSeal(chain, engine, previousBlock)
+		_, err = chain.InsertChain(types.Blocks{currentBlock})
+		assert.NoError(t, err)
+	}
+
+	// save current gov.changeSet's length for the expected value.
+	currentChangeSetLength := len(engine.governance.GetGovernanceChange())
+	assert.Equal(t, 1, currentChangeSetLength)
+
+	// block 3 is the start block of an epoch. In this test, the cache of this block's snapshot is cleared.
+	// If cache is not removed, it will just read the cache rather than making the snapshot itself.
+	block := chain.GetBlockByNumber(uint64(3))
+
+	// case [writable == false]
+	// expected result: gov.changeSet should not be modified.
+	engine.recents.Remove(block.Hash()) // assume node is restarted
+	_, err = engine.snapshot(chain, block.NumberU64(), block.Hash(), nil, false)
+	assert.Equal(t, currentChangeSetLength, len(engine.governance.GetGovernanceChange()))
+
+	// case [writable == true]
+	// expected result: gov.changeSet is modified.
+	engine.recents.Remove(block.Hash()) // assume node is restarted
+	_, err = engine.snapshot(chain, block.NumberU64(), block.Hash(), nil, true)
+	assert.Equal(t, 0, len(engine.governance.GetGovernanceChange()))
+}
+
 func TestGovernance_Votes(t *testing.T) {
 	type vote struct {
 		key   string
```

### consensus/istanbul/backend/snapshot.go
```diff
@@ -144,7 +144,7 @@ func (s *Snapshot) checkVote(address common.Address, authorize bool) bool {
 
 // apply creates a new authorization snapshot by applying the given headers to
 // the original one.
-func (s *Snapshot) apply(headers []*types.Header, gov governance.Engine, addr common.Address, policy uint64, chain consensus.ChainReader) (*Snapshot, error) {
+func (s *Snapshot) apply(headers []*types.Header, gov governance.Engine, addr common.Address, policy uint64, chain consensus.ChainReader, writable bool) (*Snapshot, error) {
 	// Allow passing in no headers for cleaner code
 	if len(headers) == 0 {
 		return s, nil
@@ -179,19 +179,20 @@ func (s *Snapshot) apply(headers []*types.Header, gov governance.Engine, addr co
 		}
 
 		if number%snap.Epoch == 0 {
-			gov.UpdateCurrentSet(number)
-			if len(header.Governance) > 0 {
-				gov.WriteGovernanceForNextEpoch(number, header.Governance)
+			if writable {
+				gov.UpdateCurrentSet(number)
+				if len(header.Governance) > 0 {
+					gov.WriteGovernanceForNextEpoch(number, header.Governance)
+				}
+				gov.ClearVotes(number)
 			}
-			gov.ClearVotes(number)
-
 			// Reload governance values because epoch changed
 			snap.Epoch, snap.Policy, snap.CommitteeSize = getGovernanceValue(gov, number)
 			snap.Votes = make([]governance.GovernanceVote, 0)
 			snap.Tally = make([]governance.GovernanceTallyItem, 0)
 		}
 
-		snap.ValSet, snap.Votes, snap.Tally = gov.HandleGovernanceVote(snap.ValSet, snap.Votes, snap.Tally, header, validator, addr)
+		snap.ValSet, snap.Votes, snap.Tally = gov.HandleGovernanceVote(snap.ValSet, snap.Votes, snap.Tally, header, validator, addr, writable)
 		if policy == uint64(params.WeightedRandom) {
 			// Snapshot of block N (Snapshot_N) should contain proposers for N+1 and following blocks.
 			// Validators for Block N+1 can be calculated based on the staking information from the previous stakingUpdateInterval block.
@@ -232,8 +233,10 @@ func (s *Snapshot) apply(headers []*types.Header, gov governance.Engine, addr co
 	}
 	snap.ValSet.SetSubGroupSize(snap.CommitteeSize)
 
-	gov.SetTotalVotingPower(snap.ValSet.TotalVotingPower())
-	gov.SetMyVotingPower(snap.getMyVotingPower(addr))
+	if writable {
+		gov.SetTotalVotingPower(snap.ValSet.TotalVotingPower())
+		gov.SetMyVotingPower(snap.getMyVotingPower(addr))
+	}
 
 	return snap, nil
 }
```

### crypto/secp256k1/curve.go
```diff
@@ -122,24 +122,11 @@ func (BitCurve *BitCurve) IsOnCurve(x, y *big.Int) bool {
 // affineFromJacobian reverses the Jacobian transform. See the comment at the
 // top of the file.
 func (BitCurve *BitCurve) affineFromJacobian(x, y, z *big.Int) (xOut, yOut *big.Int) {
-	zinv := new(big.Int).ModInverse(z, BitCurve.P)
-	//GX-TODO:	Introduce a permanent fix
-	//	When passed with x==y==z==0, ModInverse(z, BitCurve.P) results `nil` which leads to new(big.Int).Mul(nil, nil).
-	//	The above parameter condition can be easily met in cases such as adding the same elliptic curve points.
-	//
-	//	Problem:
-	// 		big.Int.Mul(nil, nil) causes SIGSEGV
-	//	Analysis:
-	// 		In Go 1.10.3, ModInverse(0, any) returns 0 (not by design though). The implementation has changed in Go 1.11
-	// 		and ModInverse explicitly returns nil. As zinv := new(big.Int).ModInverse(z, BitCurve.P) stores nil in zinv,
-	// 		zinvsq := new(big.Int).Mul(zinv, zinv) fails with SIGSEGV as it invokes new(big.Int).Mul(nil, nil).
-	//	Fix:
-	//		The following if-block is added to fix the problem temporarily. This is okay since the inverse of 0
-	//		resides in ring R = {0}.
-	if zinv == nil {
-		zinv = new(big.Int)
+	if z.Sign() == 0 {
+		return new(big.Int), new(big.Int)
 	}
 
+	zinv := new(big.Int).ModInverse(z, BitCurve.P)
 	zinvsq := new(big.Int).Mul(zinv, zinv)
 
 	xOut = new(big.Int).Mul(x, zinvsq)
@@ -152,7 +139,18 @@ func (BitCurve *BitCurve) affineFromJacobian(x, y, z *big.Int) (xOut, yOut *big.
 
 // Add returns the sum of (x1,y1) and (x2,y2)
 func (BitCurve *BitCurve) Add(x1, y1, x2, y2 *big.Int) (*big.Int, *big.Int) {
+	// If one point is at infinity, return the other point.
+	// Adding the point at infinity to any point will preserve the other point.
+	if x1.Sign() == 0 && y1.Sign() == 0 {
+		return x2, y2
+	}
+	if x2.Sign() == 0 && y2.Sign() == 0 {
+		return x1, y1
+	}
 	z := new(big.Int).SetInt64(1)
+	if x1.Cmp(x2) == 0 && y1.Cmp(y2) == 0 {
+		return BitCurve.affineFromJacobian(BitCurve.doubleJacobian(x1, y1, z))
+	}
 	return BitCurve.affineFromJacobian(BitCurve.addJacobian(x1, y1, z, x2, y2, z))
 }
 
```
