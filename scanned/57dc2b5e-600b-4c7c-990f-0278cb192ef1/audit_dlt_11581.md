# [?] Merge pull request from GHSA-68fc-7mhg-6f6c

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2024-07-04
Source: https://github.com/evmos/evmos/commit/bb2d504eec9078d6eff6981fc0cb214e8a3ca496
Type: security-commit

## Details
Merge pull request from GHSA-68fc-7mhg-6f6c

* fix(stk-precompile): update dirty state

* add create validator tests cases

* fix(distr-precompile): update dirty state

* add additional condition in isContract

* refactor test

* add more functions to the DistrCaller.sol

* fix(ics20-precompile) update dirty state

* chore(tests): add more test cases for ics20 precompile

* add multi-transfer tx test cases

* chore(tests): add more test cases for distr precompile

* Update precompiles/common/precompile.go

Signed-off-by: Tom <54514587+GAtom22@users.noreply.github.com>

* refactor getWithdrawerHexAddr func

* chore(staking-precompile): update CreateValidator and EditValidator checks

* chore(tests): update staking precompile tests

* chore(distr-precompile): remove claimRewards method

* make format

* add back claimRewards func commented out

* comment out claimRewards from distr precompile logic

* add staking test with transfer to bonded tokens acc

* chore(ibc-transfer): add escrow account to dirties

* chore(test): add test cases for ics20 precompile and escrow addr

* Update tests/nix_tests/test_ics20_precompile.py

Co-authored-by: stepit <48993133+0xstepit@users.noreply.github.com>
Signed-off-by: Tom <54514587+GAtom22@users.noreply.github.com>

* remove hardcoded exp balance

* fix(precompile): use cache ctx on stateDB

* add journal entry for precompiles

* keep only last writeFn

* add MaxPrecompileCalls limit

* refactor precompile calls logic

* remove unnecessary code

* changes based on review comments

* add StakingReverter tests

* add revert test case for distr precompile

* refactor cache ctx on stateDB

* refactor: move CommitWithCacheCtx to RunSetup

* chore: add events to snapshot

* update ICS20 tests

* fix err msg

* renamve var

* add a func on precompile cmn for journal entry

* rename var

* add comment

* update comment description

* update expected gas in ibc transfer test

* address review comments

* update comt

* tests(ics20): add helper func to setup contract

* tests(ics20): add test for nested revert

* address review comments

* add distr precompile tests

* refactor to remove UpdateDirties func

* Update precompiles/distribution/tx.go

Co-authored-by: Ramiro Carlucho <ramirocarlucho@gmail.com>
Signed-off-by: Tom <54514587+GAtom22@users.noreply.github.com>

* update vesting prec

* refactor balance change entries setter func

* add comments

* update comment

* fix sdk fork deps

* comment claimRewards method and test

* add smart contract balance check on test

* remove transient storage logic

* add edge test case with revert on storage change

* revert changes to claimRewards

* refactor var name

* refactor claimRewards logic

* refactor claimRewards logic

* update cosmos-sdk fork with latest changes (no need for store keys deep copy)

* change require with assert for invariant

* update comment

* update cosmos-sdk fork version

* update commit function with latest changes merged from main

* add changelog entry

* update commit func

* fix claimRewards comt

---------

Signed-off-by: Tom <54514587+GAtom22@users.noreply.github.com>
Signed-off-by: stepit <48993133+0xstepit@users.noreply.github.com>
Co-authored-by: stepit <48993133+0xstepit@users.noreply.github.com>
Co-authored-by: Ramiro Carlucho <ramirocarlucho@gmail.com>
Co-authored-by: stepit <stefanofrancesco.pitton@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -61,6 +61,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 - (app) [#2631](https://github.com/evmos/evmos/pull/2631) Bump IBC-go to v7.6.0 and Cosmos-SDK to v0.47.12.
 - (distribution-precompile) [#2643](https://github.com/evmos/evmos/pull/2643) Improve efficiency of reward claiming with distribution precompile.
 - (evm) [#2633](https://github.com/evmos/evmos/pull/2633) Remove `EthAccount` type and use `BaseAccount` instead.
+- (precompiles) [GHSA-68fc-7mhg-6f6c](https://github.com/evmos/evmos/<COMMIT>) Refactor precompiles to use journal entries.
 
 ### Bug Fixes
 
```

### go.mod
```diff
@@ -257,7 +257,7 @@ replace (
 	// use cosmos fork of keyring
 	github.com/99designs/keyring => github.com/cosmos/keyring v1.2.0
 	// use Cosmos-SDK fork to enable Ledger functionality
-	github.com/cosmos/cosmos-sdk => github.com/evmos/cosmos-sdk v0.47.12-evmos
+	github.com/cosmos/cosmos-sdk => github.com/evmos/cosmos-sdk v0.47.12-evmos.2
 	// use Evmos geth fork
 	github.com/ethereum/go-ethereum => github.com/evmos/go-ethereum v1.10.26-evmos-rc4
 	// Security Advisory https://github.com/advisories/GHSA-h395-qcrw-5vmq
```

### go.sum
```diff
@@ -464,8 +464,8 @@ github.com/envoyproxy/go-control-plane v0.9.9-0.20210512163311-63b5d3c536b0/go.m
 github.com/envoyproxy/go-control-plane v0.9.10-0.20210907150352-cf90f659a021/go.mod h1:AFq3mo9L8Lqqiid3OhADV3RfLJnjiw63cSpi+fDTRC0=
 github.com/envoyproxy/go-control-plane v0.10.2-0.20220325020618-49ff273808a1/go.mod h1:KJwIaB5Mv44NWtYuAOFCVOjcI94vtpEz2JU/D2v6IjE=
 github.com/envoyproxy/protoc-gen-validate v0.1.0/go.mod h1:iSmxcyjqTsJpI2R4NaDN7+kN2VEUnK/pcBlmesArF7c=
-github.com/evmos/cosmos-sdk v0.47.12-evmos h1:XyKyNboK9fLTjlY798KyfeaNxFjMIICGXNuibIALrTU=
-github.com/evmos/cosmos-sdk v0.47.12-evmos/go.mod h1:ADjORYzUQqQv/FxDi0H0K5gW/rAk1CiDR3ZKsExfJV0=
+github.com/evmos/cosmos-sdk v0.47.12-evmos.2 h1:NODyhYKCqu8JNLeR6b6ff0+TS3KYdcBiMZ4sVzXXD8I=
+github.com/evmos/cosmos-sdk v0.47.12-evmos.2/go.mod h1:ADjORYzUQqQv/FxDi0H0K5gW/rAk1CiDR3ZKsExfJV0=
 github.com/evmos/go-ethereum v1.10.26-evmos-rc4 h1:vwDVMScuB2KSu8ze5oWUuxm6v3bMUp6dL3PWvJNJY+I=
 github.com/evmos/go-ethereum v1.10.26-evmos-rc4/go.mod h1:/6CsT5Ceen2WPLI/oCA3xMcZ5sWMF/D46SjM/ayY0Oo=
 github.com/fatih/color v1.7.0/go.mod h1:Zm6kSWBoL9eyXnKyktHP6abPY2pDugNf5KwzbycvMj4=
```

### gomod2nix.toml
```diff
@@ -147,8 +147,8 @@ schema = 3
     version = "v1.0.0-beta.5"
     hash = "sha256-Fy/PbsOsd6iq0Njy3DVWK6HqWsogI+MkE8QslHGWyVg="
   [mod."github.com/cosmos/cosmos-sdk"]
-    version = "v0.47.12-evmos"
-    hash = "sha256-NqLa1Hu73zdv1yrdnppIK77RZRXpPV1MPs2pspff58g="
+    version = "v0.47.12-evmos.2"
+    hash = "sha256-xKa3vOnGloUYmgzXI93Jmt99XTkL7RRAXgl2sHN3YT8="
     replaced = "github.com/evmos/cosmos-sdk"
   [mod."github.com/cosmos/go-bip39"]
     version = "v1.0.0"
```

### precompiles/bank/bank.go
```diff
@@ -56,21 +56,18 @@ func NewPrecompile(
 
 	// NOTE: we set an empty gas configuration to avoid extra gas costs
 	// during the run execution
-	return &Precompile{
+	p := &Precompile{
 		Precompile: cmn.Precompile{
 			ABI:                  newABI,
 			KvGasConfig:          storetypes.GasConfig{},
 			TransientKVGasConfig: storetypes.GasConfig{},
 		},
 		bankKeeper:  bankKeeper,
 		erc20Keeper: erc20Keeper,
-	}, nil
-}
-
-// Address defines the address of the bank compile contract.
-// address: 0x0000000000000000000000000000000000000804
-func (Precompile) Address() common.Address {
-	return common.HexToAddress(PrecompileAddress)
+	}
+	// SetAddress defines the address of the bank compile contract.
+	p.SetAddress(common.HexToAddress(PrecompileAddress))
+	return p, nil
 }
 
 // RequiredGas calculates the precompiled contract's base gas rate.
@@ -104,7 +101,7 @@ func (p Precompile) RequiredGas(input []byte) uint64 {
 
 // Run executes the precompiled contract bank query methods defined in the ABI.
 func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz []byte, err error) {
-	ctx, stateDB, method, initialGas, args, err := p.RunSetup(evm, contract, readOnly, p.IsTransaction)
+	ctx, stateDB, snapshot, method, initialGas, args, err := p.RunSetup(evm, contract, readOnly, p.IsTransaction)
 	if err != nil {
 		return nil, err
 	}
@@ -113,10 +110,6 @@ func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz [
 	// It avoids panics and returns the out of gas error so the EVM can continue gracefully.
 	defer cmn.HandleGasError(ctx, contract, initialGas, &err)()
 
-	if err := stateDB.Commit(); err != nil {
-		return nil, err
-	}
-
 	switch method.Name {
 	// Bank queries
 	case BalancesMethod:
@@ -139,6 +132,10 @@ func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz [
 		return nil, vm.ErrOutOfGas
 	}
 
+	if err := p.AddJournalEntries(stateDB, snapshot); err != nil {
+		return nil, err
+	}
+
 	return bz, nil
 }
 
```

### precompiles/common/precompile.go
```diff
@@ -4,12 +4,14 @@ package common
 
 import (
 	"fmt"
+	"math/big"
 	"time"
 
 	storetypes "github.com/cosmos/cosmos-sdk/store/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	authzkeeper "github.com/cosmos/cosmos-sdk/x/authz/keeper"
 	"github.com/ethereum/go-ethereum/accounts/abi"
+	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core/vm"
 	"github.com/evmos/evmos/v18/x/evm/statedb"
 )
@@ -22,6 +24,35 @@ type Precompile struct {
 	ApprovalExpiration   time.Duration
 	KvGasConfig          storetypes.GasConfig
 	TransientKVGasConfig storetypes.GasConfig
+	address              common.Address
+	journalEntries       []balanceChangeEntry
+}
+
+// Operation is a type that defines if the precompile call
+// produced an addition or substraction of an account's balance
+type Operation int8
+
+const (
+	Sub Operation = iota
+	Add
+)
+
+type balanceChangeEntry struct {
+	Account common.Address
+	Amount  *big.Int
+	Op      Operation
+}
+
+func NewBalanceChangeEntry(acc common.Address, amt *big.Int, op Operation) balanceChangeEntry {
+	return balanceChangeEntry{acc, amt, op}
+}
+
+// snapshot contains all state and events previous to the precompile call
+// This is needed to allow us to revert the changes
+// during the EVM execution
+type snapshot struct {
+	MultiStore sdk.CacheMultiStore
+	Events     sdk.Events
 }
 
 // RequiredGas calculates the base minimum required gas for a transaction or a query.
@@ -44,12 +75,28 @@ func (p Precompile) RunSetup(
 	contract *vm.Contract,
 	readOnly bool,
 	isTransaction func(name string) bool,
-) (ctx sdk.Context, stateDB *statedb.StateDB, method *abi.Method, gasConfig storetypes.Gas, args []interface{}, err error) {
+) (ctx sdk.Context, stateDB *statedb.StateDB, s snapshot, method *abi.Method, gasConfig storetypes.Gas, args []interface{}, err error) {
 	stateDB, ok := evm.StateDB.(*statedb.StateDB)
 	if !ok {
-		return sdk.Context{}, nil, nil, uint64(0), nil, fmt.Errorf(ErrNotRunInEvm)
+		return sdk.Context{}, nil, s, nil, uint64(0), nil, fmt.Errorf(ErrNotRunInEvm)
+	}
+
+	// get the stateDB cache ctx
+	ctx, err = stateDB.GetCacheContext()
+	if err != nil {
+		return sdk.Context{}, nil, s, nil, uint64(0), nil, err
+	}
+
+	// take a snapshot of the current state before any changes
+	// to be able to revert the changes
+	s.MultiStore = stateDB.MultiStoreSnapshot()
+	s.Events = ctx.EventManager().Events()
+
+	// commit the current changes in the cache ctx
+	// to get the updated state for the precompile call
+	if err := stateDB.CommitWithCacheCtx(); err != nil {
+		return sdk.Context{}, nil, s, nil, uint64(0), nil, err
 	}
-	ctx = stateDB.GetContext()
 
 	// NOTE: This is a special case where the calling transaction does not specify a function name.
 	// In this case we default to a `fallback` or `receive` function on the contract.
@@ -74,20 +121,20 @@ func (p Precompile) RunSetup(
 	}
 
 	if err != nil {
-		return sdk.Context{}, nil, nil, uint64(0), nil, err
+		return sdk.Context{}, nil, s, nil, uint64(0), nil, err
 	}
 
 	// return error if trying to write to state during a read-only call
 	if readOnly && isTransaction(method.Name) {
-		return sdk.Context{}, nil, nil, uint64(0), nil, vm.ErrWriteProtection
+		return sdk.Context{}, nil, s, nil, uint64(0), nil, vm.ErrWriteProtection
 	}
 
 	// if the method type is `function` continue looking for arguments
 	if method.Type == abi.Function {
 		argsBz := contract.Input[4:]
 		args, err = method.Inputs.Unpack(argsBz)
 		if err != nil {
-			return sdk.Context{}, nil, nil, uint64(0), nil, err
+			return sdk.Context{}, nil, s, nil, uint64(0), nil, err
 		}
 	}
 
@@ -103,7 +150,7 @@ func (p Precompile) RunSetup(
 	// we need to consume the gas that was already used by the EVM
 	ctx.GasMeter().ConsumeGas(initialGas, "creating a new gas meter")
 
-	return ctx, stateDB, method, initialGas, args, nil
+	return ctx, stateDB, s, method, initialGas, args, nil
 }
 
 // HandleGasError handles the out of gas panic by resetting the gas meter and returning an error.
@@ -128,6 +175,43 @@ func HandleGasError(ctx sdk.Context, contract *vm.Contract, initialGas storetype
 	}
 }
 
+// AddJournalEntries adds the balanceChange (if corresponds)
+// and precompileCall entries on the stateDB journal
+// This allows to revert the call changes within an evm tx
+func (p Precompile) AddJournalEntries(stateDB *statedb.StateDB, s snapshot) error {
+	for _, entry := range p.journalEntries {
+		switch entry.Op {
+		case Sub:
+			// add the corresponding balance change to the journal
+			stateDB.SubBalance(entry.Account, entry.Amount)
+		case Add:
+			// add the corresponding balance change to the journal
+			stateDB.AddBalance(entry.Account, entry.Amount)
+		}
+	}
+
+	if err := stateDB.AddPrecompileFn(p.Address(), s.MultiStore, s.Events); err != nil {
+		return err
+	}
+	return nil
+}
+
+// SetBalanceChangeEntries sets the balanceChange entries
+// as the journalEntries field of the precompile.
+// These entries will be added to the stateDB's journal
+// when calling the AddJournalEntries function
+func (p *Precompile) SetBalanceChangeEntries(entries ...balanceChangeEntry) {
+	p.journalEntries = entries
+}
+
+func (p Precompile) Address() common.Address {
+	return p.address
+}
+
+func (p *Precompile) SetAddress(addr common.Address) {
+	p.address = addr
+}
+
 // emptyCallData is a helper function that returns the method to be called when the calldata is empty.
 func (p Precompile) emptyCallData(contract *vm.Contract) (method *abi.Method, err error) {
 	switch {
```

### precompiles/distribution/distribution.go
```diff
@@ -45,7 +45,7 @@ func NewPrecompile(
 		return nil, fmt.Errorf("error loading the distribution ABI %s", err)
 	}
 
-	return &Precompile{
+	p := &Precompile{
 		Precompile: cmn.Precompile{
 			ABI:                  newAbi,
 			AuthzKeeper:          authzKeeper,
@@ -55,13 +55,11 @@ func NewPrecompile(
 		},
 		stakingKeeper:      stakingKeeper,
 		distributionKeeper: distributionKeeper,
-	}, nil
-}
-
-// Address defines the address of the distribution compile contract.
-// address: 0x0000000000000000000000000000000000000801
-func (p Precompile) Address() common.Address {
-	return common.HexToAddress(PrecompileAddress)
+	}
+	// SetAddress defines the address of the distribution compile contract.
+	// address: 0x0000000000000000000000000000000000000801
+	p.SetAddress(common.HexToAddress(PrecompileAddress))
+	return p, nil
 }
 
 // RequiredGas calculates the precompiled contract's base gas rate.
@@ -84,7 +82,7 @@ func (p Precompile) RequiredGas(input []byte) uint64 {
 
 // Run executes the precompiled contract distribution methods defined in the ABI.
 func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz []byte, err error) {
-	ctx, stateDB, method, initialGas, args, err := p.RunSetup(evm, contract, readOnly, p.IsTransaction)
+	ctx, stateDB, snapshot, method, initialGas, args, err := p.RunSetup(evm, contract, readOnly, p.IsTransaction)
 	if err != nil {
 		return nil, err
 	}
@@ -93,10 +91,6 @@ func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz [
 	// It avoids panics and returns the out of gas error so the EVM can continue gracefully.
 	defer cmn.HandleGasError(ctx, contract, initialGas, &err)()
 
-	if err := stateDB.Commit(); err != nil {
-		return nil, err
-	}
-
 	switch method.Name {
 	// Custom transactions
 	case ClaimRewardsMethod:
@@ -139,6 +133,10 @@ func (p Precompile) Run(evm *vm.EVM, contract *vm.Contract, readOnly bool) (bz [
 		return nil, vm.ErrOutOfGas
 	}
 
+	if err := p.AddJournalEntries(stateDB, snapshot); err != nil {
+		return nil, err
+	}
+
 	return bz, nil
 }
 
```

### precompiles/distribution/events.go
```diff
@@ -22,16 +22,16 @@ const (
 	EventTypeWithdrawDelegatorRewards = "WithdrawDelegatorRewards"
 	// EventTypeWithdrawValidatorCommission defines the event type for the distribution WithdrawValidatorCommissionMethod transaction.
 	EventTypeWithdrawValidatorCommission = "WithdrawValidatorCommission"
-	// EventTypeClaimRewards defines the event type for the distribution ClaimRewardsMethod transaction.
-	EventTypeClaimRewards = "ClaimRewards"
 	// EventTypeFundCommunityPool defines the event type for the distribution FundCommunityPoolMethod transaction.
 	EventTypeFundCommunityPool = "FundCommunityPool"
+	// EventTypeClaimRewards defines the event type for the distribution ClaimRewardsMethod transaction.
+	EventTypeClaimRewards = "ClaimRewards"
 )
 
 // EmitClaimRewardsEvent creates a new event emitted on a ClaimRewards transaction.
 func (p Precompile) EmitClaimRewardsEvent(ctx sdk.Context, stateDB vm.StateDB, delegatorAddress common.Address, totalCoins sdk.Coins) error {
 	// Prepare the event topics
-	event := p.ABI.Events[EventTypeClaimRewards]
+	event := p.Events[EventTypeClaimRewards]
 	topics := make([]common.Hash, 2)
 
 	// The first topic is always the signature of the event.
```

### precompiles/distribution/integration_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"cosmossdk.io/math"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/types/query"
+	distrkeeper "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
 	distrtypes "github.com/cosmos/cosmos-sdk/x/distribution/types"
 	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
 	"github.com/ethereum/go-ethereum/common"
@@ -20,6 +21,7 @@ import (
 	evmosutil "github.com/evmos/evmos/v18/testutil"
 	testutiltx "github.com/evmos/evmos/v18/testutil/tx"
 	"github.com/evmos/evmos/v18/utils"
+	evmtypes "github.com/evmos/evmos/v18/x/evm/types"
 
 	//nolint:revive // dot imports are fine for Ginkgo
 	. "github.com/onsi/ginkgo/v2"
@@ -52,6 +54,9 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 	BeforeEach(func() {
 		s.SetupTest()
 
+		initialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+		fmt.Println("Fist Before each: ", initialBalance)
+
 		// set the default call arguments
 		defaultCallArgs = contracts.CallArgs{
 			ContractAddr: s.precompile.Address(),
@@ -60,10 +65,13 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 		}
 
 		defaultLogCheck = testutil.LogCheckArgs{
-			ABIEvents: s.precompile.ABI.Events,
+			ABIEvents: s.precompile.Events,
 		}
 		passCheck = defaultLogCheck.WithExpPass(true)
 		outOfGasCheck = defaultLogCheck.WithErrContains(vm.ErrOutOfGas.Error())
+
+		initialBalance = s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+		fmt.Println("Fist Before each: ", initialBalance)
 	})
 
 	// =====================================
@@ -321,9 +329,8 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 			err = s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), contractAddr.Bytes())
 			Expect(err).To(BeNil())
 
-			// initial balance should be the initial amount minus the staked amount used to create the validator, minus fees paid for deploying contract
+			// get validator initial balance
 			initialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
-			Expect(initialBalance.Amount).To(Equal(math.NewInt(4997457315624999900)))
 
 			withdrawCommissionArgs := defaultWithdrawCommissionArgs.
 				WithArgs(valAddr.String()).
@@ -358,12 +365,15 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 		//
 		// NOTE: this has to be populated in the BeforeEach block because the private key otherwise is not yet initialized.
 		var defaultClaimRewardsArgs contracts.CallArgs
+		// starting balance minus delegated tokens
 		startingBalance := math.NewInt(5e18)
 		expectedBalance := math.NewInt(8999665039062500000)
 
 		BeforeEach(func() {
 			// set the default call arguments
 			defaultClaimRewardsArgs = defaultCallArgs.WithMethodName(distribution.ClaimRewardsMethod)
+			initialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+			fmt.Println("BeforeEach: ", initialBalance)
 			s.prepareStakingRewards(stakingRewards{s.address.Bytes(), s.validators[0], rewards})
 			s.prepareStakingRewards(stakingRewards{s.address.Bytes(), s.validators[1], rewards})
 		})
@@ -393,7 +403,6 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 			Expect(finalBalance.Amount.Equal(expectedBalance)).To(BeTrue(), "expected final balance to be equal to initial balance + rewards - fees")
 		})
 	})
-
 	// =====================================
 	// 				QUERIES
 	// =====================================
@@ -627,6 +636,15 @@ var _ = Describe("Calling distribution precompile from EOA", func() {
 })
 
 var _ = Describe("Calling distribution precompile from another contract", func() {
+	// testCase is a struct used for cases of contracts calls that have some operation
+	// performed before and/or after the precompile call
+	type testCase struct {
+		delegator  *common.Address
+		withdrawer *common.Address
+		before     bool
+		after      bool
+	}
+
 	var (
 		// initBalanceAmt is the initial balance for testing
 		initBalanceAmt = math.NewInt(5000000000000000000)
@@ -800,10 +818,10 @@ var _ = Describe("Calling distribution precompile from another contract", func()
 			Expect(finalBalance.Amount.GT(initialBalance.Amount)).To(BeTrue(), "expected final balance to be greater than initial balance after withdrawing rewards")
 		})
 
-		It("should withdraw rewards successfully to the new withdrawer address", func() {
-			initialBalance := s.app.BankKeeper.GetBalance(s.ctx, differentAddr.Bytes(), s.bondDenom)
+		DescribeTable("should withdraw rewards successfully to the new withdrawer address", func(tc testCase) {
+			initialBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
 			// Set new withdrawer address
-			err := s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), differentAddr.Bytes())
+			err := s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), tc.withdrawer.Bytes())
 			Expect(err).To(BeNil())
 
 			withdrawDelRewardsArgs := defaultWithdrawDelRewardsArgs.WithArgs(
@@ -817,8 +835,178 @@ var _ = Describe("Calling distribution precompile from another contract", func()
 			Expect(err).To(BeNil(), "error while calling the smart contract: %v", err)
 
 			// should increase balance by rewards
-			finalBalance := s.app.BankKeeper.GetBalance(s.ctx, differentAddr.Bytes(), s.bondDenom)
+			finalBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
 			Expect(finalBalance.Amount.GT(initialBalance.Amount)).To(BeTrue(), "expected final balance to be greater than initial balance after withdrawing rewards")
+		},
+			Entry("withdrawer addr is existing acc", testCase{
+				withdrawer: &differentAddr,
+			}),
+			Entry("withdrawer addr is non-existing acc", testCase{
+				withdrawer: func() *common.Address {
+					addr := testutiltx.GenerateAddress()
+					return &addr
+				}(),
+			}),
+		)
+
+		// Specific BeforeEach for table-driven tests
+		Context("Table-driven tests for Withdraw Delegator Rewards", func() {
+			var (
+				args                   contracts.CallArgs
+				contractInitialBalance = math.NewInt(100)
+			)
+			BeforeEach(func() {
+				args = defaultWithdrawDelRewardsArgs.
+					WithMethodName("testWithdrawDelegatorRewardsWithTransfer").
+					WithGasPrice(gasPrice)
+
+				// send some funds to the contract
+				err := evmosutil.FundAccountWithBaseDenom(s.ctx, s.app.BankKeeper, contractAddr.Bytes(), contractInitialBalance.Int64())
+				Expect(err).To(BeNil())
+			})
+
+			DescribeTable("withdraw delegation rewards with internal transfers to delegator - should withdraw rewards successfully to the withdrawer address",
+				func(tc testCase) {
+					withdrawerInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+					if tc.withdrawer != nil {
+						// Set new withdrawer address
+						err := s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), tc.withdrawer.Bytes())
+						Expect(err).To(BeNil())
+						withdrawerInitialBalance = s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+					}
+
+					delInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+
+					// get the pending rewards to claim
+					qr := distrkeeper.Querier{Keeper: s.app.DistrKeeper}
+					qRes, err := qr.DelegationRewards(s.ctx, &distrtypes.QueryDelegationRewardsRequest{DelegatorAddress: sdk.AccAddress(s.address.Bytes()).String(), ValidatorAddress: s.validators[0].OperatorAddress})
+					Expect(err).To(BeNil())
+					expRewards := qRes.Rewards.AmountOf(s.bondDenom).TruncateInt()
+
+					withdrawDelRewardsArgs := args.WithArgs(
+						s.address, s.validators[0].OperatorAddress, tc.before, tc.after,
+					)
+
+					logCheckArgs := passCheck.
+						WithExpEvents(distribution.EventTypeWithdrawDelegatorRewards)
+
+					res, _, err := contracts.CallContractAndCheckLogs(s.ctx, s.app, withdrawDelRewardsArgs, logCheckArgs)
+					Expect(err).To(BeNil(), "error while calling the smart contract: %v", err)
+					fees := math.NewIntFromBigInt(gasPrice).MulRaw(res.GasUsed)
+
+					// check balances
+					contractTransferredAmt := math.ZeroInt()
+					for _, transferred := range []bool{tc.before, tc.after} {
+						if transferred {
+							contractTransferredAmt = contractTransferredAmt.AddRaw(15)
+						}
+					}
+					// contract balance be updated according to the transferred amount
+					contractFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, contractAddr.Bytes(), s.bondDenom)
+					Expect(contractFinalBalance.Amount).To(Equal(contractInitialBalance.Sub(contractTransferredAmt)))
+
+					expDelFinalBalance := delInitialBalance.Amount.Sub(fees).Add(contractTransferredAmt).Add(expRewards)
+					if tc.withdrawer != nil {
+						expDelFinalBalance = delInitialBalance.Amount.Sub(fees).Add(contractTransferredAmt)
+						expWithdrawerFinalBalance := withdrawerInitialBalance.Amount.Add(expRewards)
+						// withdrawer balance should have the rewards
+						withdrawerFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+						Expect(withdrawerFinalBalance.Amount).To(Equal(expWithdrawerFinalBalance), "expected final balance to be greater than initial balance after withdrawing rewards")
+					}
+
+					// delegator balance should have the transferred amt - fees + rewards (when is the withdrawer)
+					delFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+					Expect(delFinalBalance.Amount).To(Equal(expDelFinalBalance), "expected final balance to be greater than initial balance after withdrawing rewards")
+				},
+
+				Entry("delegator == withdrawer - with internal transfers before and after precompile call", testCase{
+					before: true,
+					after:  true,
+				}),
+
+				Entry("delegator == withdrawer - with internal transfers before precompile call", testCase{
+					before: true,
+					after:  false,
+				}),
+
+				Entry("delegator == withdrawer - with internal transfers after precompile call", testCase{
+					before: false,
+					after:  true,
+				}),
+				Entry("delegator != withdrawer - with internal transfers before and after precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     true,
+					after:      true,
+				}),
+
+				Entry("delegator != withdrawer - with internal transfers before precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     true,
+					after:      false,
+				}),
+
+				Entry("delegator != withdrawer - with internal transfers after precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     false,
+					after:      true,
+				}),
+			)
+
+			DescribeTable("should revert withdraw rewards successfully and update correspondingly the withdrawer and contract's balances", func(tc testCase) {
+				// get the pending rewards to claim
+				qr := distrkeeper.Querier{Keeper: s.app.DistrKeeper}
+				qRes, err := qr.DelegationRewards(s.ctx, &distrtypes.QueryDelegationRewardsRequest{DelegatorAddress: sdk.AccAddress(s.address.Bytes()).String(), ValidatorAddress: s.validators[0].OperatorAddress})
+				Expect(err).To(BeNil())
+				initRewards := qRes.Rewards.AmountOf(s.bondDenom).TruncateInt()
+
+				delInitBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+				withdrawerInitBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+				// Set new withdrawer address
+				err = s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), tc.withdrawer.Bytes())
+				Expect(err).To(BeNil())
+
+				// update args to call the corresponding contract method
+				callArgs := args.
+					WithMethodName("revertWithdrawRewardsAndTransfer").
+					WithArgs(
+						s.address, *tc.withdrawer, s.validators[0].OperatorAddress, true,
+					)
+
+				res, _, err := contracts.CallContractAndCheckLogs(s.ctx, s.app, callArgs, passCheck)
+				Expect(err).To(BeNil(), "error while calling the smart contract: %v", err)
+				fees := math.NewIntFromBigInt(gasPrice).MulRaw(res.GasUsed)
+
+				// check balances
+				contractTransferredAmt := math.NewInt(15)
+				// contract balance be updated according to the transferred amount
+				contractFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, contractAddr.Bytes(), s.bondDenom)
+				Expect(contractFinalBalance.Amount).To(Equal(contractInitialBalance.Sub(contractTransferredAmt)))
+
+				// delegator balance should be initial_balance - fees
+				delFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+				Expect(delFinalBalance.Amount).To(Equal(delInitBalance.Amount.Sub(fees)))
+
+				// withdrawer balance should increase by the transferred amount only
+				// the rewards withdrawal should revert
+				withdrawerFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+				Expect(withdrawerFinalBalance.Amount).To(Equal(withdrawerInitBalance.Amount.Add(contractTransferredAmt)), "expected final balance to be greater than initial balance after withdrawing rewards")
+
+				// rewards to claim should remain unchanged
+				qRes, err = qr.DelegationRewards(s.ctx, &distrtypes.QueryDelegationRewardsRequest{DelegatorAddress: sdk.AccAddress(s.address.Bytes()).String(), ValidatorAddress: s.validators[0].OperatorAddress})
+				Expect(err).To(BeNil())
+				finalRewards := qRes.Rewards.AmountOf(s.bondDenom).TruncateInt()
+				Expect(finalRewards).To(Equal(initRewards))
+			},
+				Entry("withdrawer addr is existing acc", testCase{
+					withdrawer: &differentAddr,
+				}),
+				Entry("withdrawer addr is non-existing acc", testCase{
+					withdrawer: func() *common.Address {
+						addr := testutiltx.GenerateAddress()
+						return &addr
+					}(),
+				}),
+			)
 		})
 	})
 
@@ -887,6 +1075,75 @@ var _ = Describe("Calling distribution precompile from another contract", func()
 			finalDelegatorBalance := s.app.BankKeeper.GetBalance(s.ctx, contractAddr.Bytes(), s.bondDenom)
 			Expect(finalDelegatorBalance.Amount.Equal(initialBalance.Amount)).To(BeTrue(), "expected delegator final balance remain unchanged after withdrawing rewards to withdrawer")
 		})
+
+		Context("Withdraw Delegator Rewards with another smart contract (different than the contract calling the precompile) as delegator", func() {
+			var (
+				delContractAddr        common.Address
+				args                   contracts.CallArgs
+				contractInitialBalance = math.NewInt(100)
+			)
+			BeforeEach(func() {
+				args = defaultWithdrawDelRewardsArgs.
+					WithMethodName("testWithdrawDelegatorRewardsWithTransfer").
+					WithGasPrice(gasPrice)
+
+				// deploy a contract to use as delegator contract
+				delegatorContract, err := contracts.LoadInterchainSenderContract()
+				Expect(err).To(BeNil())
+
+				delContractAddr, err = s.DeployContract(delegatorContract)
+				Expect(err).To(BeNil(), "error while deploying the smart contract: %v", err)
+
+				// send some funds to the contract
+				err = evmosutil.FundAccountWithBaseDenom(s.ctx, s.app.BankKeeper, contractAddr.Bytes(), contractInitialBalance.Int64())
+				Expect(err).To(BeNil())
+
+				// set some rewards for the delegator contract
+				s.prepareStakingRewards([]stakingRewards{
+					{
+						Delegator: delContractAddr.Bytes(),
+						Validator: s.validators[0],
+						RewardAmt: rewards,
+					},
+				}...)
+			})
+
+			It("should NOT allow to withdraw rewards", func() {
+				txSenderInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+				delInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, delContractAddr.Bytes(), s.bondDenom)
+
+				// get the pending rewards to claim
+				qr := distrkeeper.Querier{Keeper: s.app.DistrKeeper}
+				qRes, err := qr.DelegationRewards(s.ctx, &distrtypes.QueryDelegationRewardsRequest{DelegatorAddress: sdk.AccAddress(delContractAddr.Bytes()).String(), ValidatorAddress: s.validators[0].OperatorAddress})
+				Expect(err).To(BeNil())
+				expRewards := qRes.Rewards.AmountOf(s.bondDenom).TruncateInt()
+
+				withdrawDelRewardsArgs := args.WithArgs(
+					delContractAddr, s.validators[0].OperatorAddress, true, true,
+				)
+
+				_, _, err = contracts.CallContractAndCheckLogs(s.ctx, s.app, withdrawDelRewardsArgs, execRevertedCheck)
+				Expect(err).NotTo(BeNil(), "error while calling the smart contract: %v", err)
+
+				// check balances
+				// tx signer final balance should be the initial balance - fees
+				txSignerFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+				Expect(txSignerFinalBalance.Amount.LT(txSenderInitialBalance.Amount)).To(BeTrue())
+
+				// contract balance be updated according to the transferred amount
+				contractFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, contractAddr.Bytes(), s.bondDenom)
+				Expect(contractFinalBalance.Amount).To(Equal(contractInitialBalance))
+
+				// delegator balance should have the transferred amt + rewards (when is the withdrawer)
+				delFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, delContractAddr.Bytes(), s.bondDenom)
+				Expect(delFinalBalance.Amount).To(Equal(delInitialBalance.Amount))
+
+				// delegation rewards should remain unchanged
+				qRes, err = qr.DelegationRewards(s.ctx, &distrtypes.QueryDelegationRewardsRequest{DelegatorAddress: sdk.AccAddress(delContractAddr.Bytes()).String(), ValidatorAddress: s.validators[0].OperatorAddress})
+				Expect(err).To(BeNil())
+				Expect(qRes.Rewards.AmountOf(s.bondDenom).TruncateInt()).To(Equal(expRewards))
+			})
+		})
 	})
 
 	Context("withdrawValidatorCommission", func() {
@@ -995,6 +1252,138 @@ var _ = Describe("Calling distribution precompile from another contract", func()
 			expFinal := initialBalance.Amount.Int64() - fees
 			Expect(finalBalance.Amount).To(Equal(math.NewInt(expFinal)), "expected final balance to be equal to initial balance  - fees")
 		})
+
+		// Specific BeforeEach for table-driven tests
+		Context("Table-driven tests for Withdraw Validator Commission", func() {
+			var (
+				args                   contracts.CallArgs
+				contractInitialBalance = math.NewInt(100)
+			)
+			BeforeEach(func() {
+				args = defaultWithdrawValCommArgs.
+					WithMethodName("testWithdrawValidatorCommissionWithTransfer").
+					WithGasPrice(gasPrice)
+
+				// send some funds to the contract
+				err := evmosutil.FundAccountWithBaseDenom(s.ctx, s.app.BankKeeper, contractAddr.Bytes(), contractInitialBalance.Int64())
+				Expect(err).To(BeNil())
+			})
+
+			DescribeTable("withdraw validator commission with state changes in withdrawer - should withdraw commission successfully to the withdrawer address",
+				func(tc testCase) {
+					withdrawerAddr := s.address
+					withdrawerInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+					if tc.withdrawer != nil {
+						withdrawerAddr = *tc.withdrawer
+						// Set new withdrawer address
+						err := s.app.DistrKeeper.SetWithdrawAddr(s.ctx, s.address.Bytes(), tc.withdrawer.Bytes())
+						Expect(err).To(BeNil())
+						withdrawerInitialBalance = s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+					}
+
+					valInitialBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+
+					// get the pending comission to claim
+					valAccAddr := sdk.ValAddress(s.address.Bytes())
+					qr := distrkeeper.Querier{Keeper: s.app.DistrKeeper}
+					qRes, err := qr.ValidatorCommission(s.ctx, &distrtypes.QueryValidatorCommissionRequest{ValidatorAddress: valAccAddr.String()})
+					Expect(err).To(BeNil())
+					expCommission := qRes.Commission.Commission.AmountOf(s.bondDenom).TruncateInt()
+
+					withdrawValCommissionArgs := args.WithArgs(
+						valAccAddr.String(), withdrawerAddr, tc.before, tc.after,
+					)
+
+					logCheckArgs := passCheck.
+						WithExpEvents(distribution.EventTypeWithdrawValidatorCommission)
+
+					res, _, err := contracts.CallContractAndCheckLogs(s.ctx, s.app, withdrawValCommissionArgs, logCheckArgs)
+					Expect(err).To(BeNil(), "error while calling the smart contract: %v", err)
+					fees := math.NewIntFromBigInt(gasPrice).MulRaw(res.GasUsed)
+
+					// calculate the transferred amt during the call
+					contractTransferredAmt := math.ZeroInt()
+					for _, transferred := range []bool{tc.before, tc.after} {
+						if transferred {
+							contractTransferredAmt = contractTransferredAmt.AddRaw(15)
+						}
+					}
+
+					// check balances
+					expContractFinalBalance := contractInitialBalance.Sub(contractTransferredAmt)
+					expValFinalBalance := valInitialBalance.Amount.Sub(fees).Add(contractTransferredAmt).Add(expCommission)
+					if tc.withdrawer != nil {
+						expValFinalBalance = valInitialBalance.Amount.Sub(fees)
+						if *tc.withdrawer == contractAddr {
+							// no internal transfers if the contract itself is the withdrawer
+							expContractFinalBalance = contractInitialBalance.Add(expCommission)
+						} else {
+							expWithdrawerFinalBalance := withdrawerInitialBalance.Amount.Add(expCommission).Add(contractTransferredAmt)
+							// withdrawer balance should have the rewards
+							withdrawerFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, tc.withdrawer.Bytes(), s.bondDenom)
+							Expect(withdrawerFinalBalance.Amount).To(Equal(expWithdrawerFinalBalance), "expected final balance to be greater than initial balance after withdrawing rewards")
+						}
+					}
+
+					// contract balance be updated according to the transferred amount
+					contractFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, contractAddr.Bytes(), s.bondDenom)
+					Expect(contractFinalBalance.Amount).To(Equal(expContractFinalBalance))
+
+					// validator balance should have the transferred amt - fees + rewards (when is the withdrawer)
+					valFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, s.address.Bytes(), s.bondDenom)
+					Expect(valFinalBalance.Amount).To(Equal(expValFinalBalance), "expected final balance to be greater than initial balance after withdrawing rewards")
+				},
+
+				Entry("validator == withdrawer - with internal transfers before and after precompile call", testCase{
+					before: true,
+					after:  true,
+				}),
+
+				Entry("validator == withdrawer - with internal transfers before precompile call", testCase{
+					before: true,
+					after:  false,
+				}),
+
+				Entry("validator == withdrawer - with internal transfers after precompile call", testCase{
+					before: false,
+					after:  true,
+				}),
+				Entry("validator != withdrawer - with internal transfers before and after precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     true,
+					after:      true,
+				}),
+
+				Entry("validator != withdrawer - with internal transfers before precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     true,
+					after:      false,
+				}),
+
+				Entry("validator != withdrawer - with internal transfers after precompile call", testCase{
+					withdrawer: &differentAddr,
+					before:     false,
+					after:      true,
+				}),
+				Entry("contract as withdrawer - with contract state change before and after precompile call", testCase{
+					withdrawer: &contractAddr,
+					before:     true,
+					after:      true,
+				}),
+
+				Entry("contract as withdrawer - with contract state change before precompile call", testCase{
+					withdrawer: &contractAddr,
+					before:     true,
+					after:      false,
+				}),
+
+				Entry("contract as withdrawer - with contract state change after precompile call", testCase{
+					withdrawer: &contractAddr,
+					before:     false,
+					after:      true,
+				}),
+			)
+		})
 	})
 
 	Context("claimRewards", func() {
@@ -1465,6 +1854,45 @@ var _ = Describe("Calling distribution precompile from another contract", func()
 				Expect(1).To(Equal(len(out.Total)))
 				Expect(expDelegationRewards).To(Equal(out.Total[0].Amount.Int64()))
 			})
+
+			Context("query call with revert - all changes should revert to corresponding stateDB snapshot", func() {
+				var (
+					reverterContract           evmtypes.CompiledContract
+					reverterAddr               common.Address
+					testContractInitialBalance = math.NewInt(1000)
+				)
+				BeforeEach(func() {
+					var err error
+					// Deploy Reverter contract
+					reverterContract, err = contracts.LoadReverterContract()
+					Expect(err).To(BeNil(), "error while loading the Reverter contract")
+
+					reverterAddr, err = s.DeployContract(reverterContract)
+					Expect(err).To(BeNil(), "error while deploying the Reverter contract")
+					s.NextBlock()
+
+					// send some funds to the Reverter contracts to transfer to the
+					// delegator during the tx
+					err = evmosutil.FundAccount(s.ctx, s.app.BankKeeper, reverterAddr.Bytes(), sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, testContractInitialBalance)))
+					Expect(err).To(BeNil(), "error while funding the smart contract: %v", err)
+				})
+
+				It("should revert the execution - Reverter contract", func() {
+					args := contracts.CallArgs{
+						ContractAddr: reverterAddr,
+						ContractABI:  reverterContract.ABI,
+						PrivKey:      s.privKey,
+						MethodName:   "run",
+						GasPrice:     gasPrice,
+					}
+
+					_, _, err := contracts.CallContractAndCheckLogs(s.ctx, s.app, args, execRevertedCheck)
+					Expect(err).NotTo(BeNil(), "error while calling the smart contract: %v", err)
+
+					contractFinalBalance := s.app.BankKeeper.GetBalance(s.ctx, reverterAddr.Bytes(), s.bondDenom)
+					Expect(contractFinalBalance.Amount).To(Equal(testContractInitialBalance))
+				})
+			})
 		})
 
 		Context("get all delegator validators", func() {
```

### precompiles/distribution/tx.go
```diff
@@ -7,15 +7,13 @@ import (
 	"fmt"
 
 	"github.com/evmos/evmos/v18/utils"
-	"github.com/evmos/evmos/v18/x/evm/statedb"
 
 	cmn "github.com/evmos/evmos/v18/precompiles/common"
 
 	"github.com/ethereum/go-ethereum/common"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	distributionkeeper "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
-	distributiontypes "github.com/cosmos/cosmos-sdk/x/distribution/types"
 	"github.com/ethereum/go-ethereum/accounts/abi"
 	"github.com/ethereum/go-ethereum/core/vm"
 )
@@ -30,10 +28,10 @@ const (
 	// WithdrawValidatorCommissionMethod defines the ABI method name for the distribution
 	// WithdrawValidatorCommission transaction.
 	WithdrawValidatorCommissionMethod = "withdrawValidatorCommission"
-	// ClaimRewardsMethod defines the ABI method name for the custom ClaimRewards transaction
-	ClaimRewardsMethod = "claimRewards"
 	// FundCommunityPoolMethod defines the ABI method name for the fundCommunityPool transaction
 	FundCommunityPoolMethod = "fundCommunityPool"
+	// ClaimRewardsMethod defines the ABI method name for the custom ClaimRewards transaction
+	ClaimRewardsMethod = "claimRewards"
 )
 
 // ClaimRewards claims the rewards accumulated by a delegator from multiple or all validators.
@@ -57,7 +55,7 @@ func (p Precompile) ClaimRewards(
 
 	// If the contract is the delegator, we don't need an origin check
 	// Otherwise check if the origin matches the delegator address
-	isContractDelegator := contract.CallerAddress == delegatorAddr
+	isContractDelegator := contract.CallerAddress == delegatorAddr && origin != delegatorAddr
 	if !isContractDelegator && origin != delegatorAddr {
 		return nil, fmt.Errorf(cmn.ErrDelegatorDifferentOrigin, origin.String(), delegatorAddr.String())
 	}
@@ -80,18 +78,13 @@ func (p Precompile) ClaimRewards(
 		totalCoins = totalCoins.Add(coins...)
 	}
 
-	// rewards go to the withdrawer address
-	// check if it is a contract
-	ok, withdrawerHexAddr, err := p.isContractWithdrawer(ctx, stateDB, sdk.AccAddress(delegatorAddr.Bytes()))
-	if err != nil {
-		return nil, err
-	}
-
 	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB.
 	// This prevents the stateDB from overwriting the changed balance in the bank keeper when committing the EVM state.
 	// this happens when the precompile is called from a smart contract
-	if ok && contract.CallerAddress != origin {
-		stateDB.(*statedb.StateDB).AddBalance(withdrawerHexAddr, totalCoins[0].Amount.BigInt())
+	if contract.CallerAddress != origin {
+		// rewards go to the withdrawer address
+		withdrawerHexAddr := p.getWithdrawerHexAddr(ctx, delegatorAddr)
+		p.SetBalanceChangeEntries(cmn.NewBalanceChangeEntry(withdrawerHexAddr, totalCoins.AmountOf(utils.BaseDenom).BigInt(), cmn.Add))
 	}
 
 	if err := p.EmitClaimRewardsEvent(ctx, stateDB, delegatorAddr, totalCoins); err != nil {
@@ -117,7 +110,7 @@ func (p Precompile) SetWithdrawAddress(
 
 	// If the contract is the delegator, we don't need an origin check
 	// Otherwise check if the origin matches the delegator address
-	isContractDelegator := contract.CallerAddress == delegatorHexAddr
+	isContractDelegator := contract.CallerAddress == delegatorHexAddr && origin != delegatorHexAddr
 	if !isContractDelegator && origin != delegatorHexAddr {
 		return nil, fmt.Errorf(cmn.ErrDelegatorDifferentOrigin, origin.String(), delegatorHexAddr.String())
 	}
@@ -135,7 +128,7 @@ func (p Precompile) SetWithdrawAddress(
 }
 
 // WithdrawDelegatorRewards withdraws the rewards of a delegator from a single validator.
-func (p Precompile) WithdrawDelegatorRewards(
+func (p *Precompile) WithdrawDelegatorRewards(
 	ctx sdk.Context,
 	origin common.Address,
 	contract *vm.Contract,
@@ -150,7 +143,7 @@ func (p Precompile) WithdrawDelegatorRewards(
 
 	// If the contract is the delegator, we don't need an origin check
 	// Otherwise check if the origin matches the delegator address
-	isContractDelegator := contract.CallerAddress == delegatorHexAddr
+	isContractDelegator := contract.CallerAddress == delegatorHexAddr && origin != delegatorHexAddr
 	if !isContractDelegator && origin != delegatorHexAddr {
 		return nil, fmt.Errorf(cmn.ErrDelegatorDifferentOrigin, origin.String(), delegatorHexAddr.String())
 	}
@@ -161,17 +154,13 @@ func (p Precompile) WithdrawDelegatorRewards(
 		return nil, err
 	}
 
-	// rewards go to the withdrawer address
-	// check if it is a contract
-	ok, withdrawerHexAddr, err := p.isContractWithdrawer(ctx, stateDB, sdk.AccAddress(delegatorHexAddr.Bytes()))
-	if err != nil {
-		return nil, err
-	}
-
-	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB.
+	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB
+	// when calling the precompile from a smart contract
 	// This prevents the stateDB from overwriting the changed balance in the bank keeper when committing the EVM state.
-	if ok && contract.CallerAddress != origin {
-		stateDB.(*statedb.StateDB).AddBalance(withdrawerHexAddr, res.Amount[0].Amount.BigInt())
+	if contract.CallerAddress != origin {
+		// rewards go to the withdrawer address
+		withdrawerHexAddr := p.getWithdrawerHexAddr(ctx, delegatorHexAddr)
+		p.SetBalanceChangeEntries(cmn.NewBalanceChangeEntry(withdrawerHexAddr, res.Amount[0].Amount.BigInt(), cmn.Add))
 	}
 
 	if err = p.EmitWithdrawDelegatorRewardsEvent(ctx, stateDB, delegatorHexAddr, msg.ValidatorAddress, res.Amount); err != nil {
@@ -182,7 +171,7 @@ func (p Precompile) WithdrawDelegatorRewards(
 }
 
 // WithdrawValidatorCommission withdraws the rewards of a validator.
-func (p Precompile) WithdrawValidatorCommission(
+func (p *Precompile) WithdrawValidatorCommission(
 	ctx sdk.Context,
 	origin common.Address,
 	contract *vm.Contract,
@@ -197,7 +186,7 @@ func (p Precompile) WithdrawValidatorCommission(
 
 	// If the contract is the validator, we don't need an origin check
 	// Otherwise check if the origin matches the validator address
-	isContractValidator := contract.CallerAddress == validatorHexAddr
+	isContractValidator := contract.CallerAddress == validatorHexAddr && origin != validatorHexAddr
 	if !isContractValidator && origin != validatorHexAddr {
 		return nil, fmt.Errorf(cmn.ErrDelegatorDifferentOrigin, origin.String(), validatorHexAddr.String())
 	}
@@ -208,16 +197,13 @@ func (p Precompile) WithdrawValidatorCommission(
 		return nil, err
 	}
 
-	// commissions go to the withdrawer address
-	// check if it is a contract
-	ok, withdrawerHexAddr, err := p.isContractWithdrawer(ctx, stateDB, sdk.AccAddress(validatorHexAddr.Bytes()))
-	if err != nil {
-		return nil, err
-	}
-	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB.
+	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB
+	// when calling the precompile from a smart contract
 	// This prevents the stateDB from overwriting the changed balance in the bank keeper when committing the EVM state.
-	if ok && contract.CallerAddress != origin {
-		stateDB.(*statedb.StateDB).AddBalance(withdrawerHexAddr, res.Amount[0].Amount.BigInt())
+	if contract.CallerAddress != origin {
+		// commissions go to the withdrawer address
+		withdrawerHexAddr := p.getWithdrawerHexAddr(ctx, validatorHexAddr)
+		p.SetBalanceChangeEntries(cmn.NewBalanceChangeEntry(withdrawerHexAddr, res.Amount[0].Amount.BigInt(), cmn.Add))
 	}
 
 	if err = p.EmitWithdrawValidatorCommissionEvent(ctx, stateDB, msg.ValidatorAddress, res.Amount); err != nil {
@@ -228,7 +214,7 @@ func (p Precompile) WithdrawValidatorCommission(
 }
 
 // FundCommunityPool directly fund the community pool
-func (p Precompile) FundCommunityPool(
+func (p *Precompile) FundCommunityPool(
 	ctx sdk.Context,
 	origin common.Address,
 	contract *vm.Contract,
@@ -243,7 +229,7 @@ func (p Precompile) FundCommunityPool(
 
 	// If the contract is the depositor, we don't need an origin check
 	// Otherwise check if the origin matches the depositor address
-	isContractDepositor := contract.CallerAddress == depositorHexAddr
+	isContractDepositor := contract.CallerAddress == depositorHexAddr && origin != depositorHexAddr
 	if !isContractDepositor && origin != depositorHexAddr {
 		return nil, fmt.Errorf(cmn.ErrSpenderDifferentOrigin, origin.String(), depositorHexAddr.String())
 	}
@@ -254,10 +240,11 @@ func (p Precompile) FundCommunityPool(
 		return nil, err
 	}
 
-	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB.
+	// NOTE: This ensures that the changes in the bank keeper are correctly mirrored to the EVM stateDB
+	// when calling the precompile from a smart contract
 	// This prevents the stateDB from overwriting the changed balance in the bank keeper when committing the EVM state.
-	if isContractDepositor {
-		stateDB.(*statedb.StateDB).SubBalance(contract.CallerAddress, msg.Amount.AmountOf(utils.BaseDenom).BigInt())
+	if contract.CallerAddress != origin {
+		p.SetBalanceChangeEntries(cmn.NewBalanceChangeEntry(depositorHexAddr, msg.Amount.AmountOf(utils.BaseDenom).BigInt(), cmn.Sub))
 	}
 
 	if err = p.EmitFundCommunityPoolEvent(ctx, stateDB, depositorHexAddr, msg.Amount); err != nil {
@@ -267,27 +254,9 @@ func (p Precompile) FundCommunityPool(
 	return method.Outputs.Pack(true)
 }
 
-// isContractWithdrawer is a helper function to check if the withdrawer address of a
-// delegator is a smart contract. It returns a boolean specifying if the withdrawer
-// is a smart contract, and the corresponding withdrawer hex address
-func (p Precompile) isContractWithdrawer(ctx sdk.Context, stateDB vm.StateDB, delegatorAccAddr sdk.AccAddress) (bool, common.Address, error) {
-	// check if withdrawer address is a contract
-	querier := distributionkeeper.Querier{Keeper: p.distributionKeeper}
-	qRes, err := querier.DelegatorWithdrawAddress(
-		ctx,
-		&distributiontypes.QueryDelegatorWithdrawAddressRequest{
-			DelegatorAddress: delegatorAccAddr.String(),
-		},
-	)
-	if err != nil {
-		return false, common.Address{}, err
-	}
-
-	withdrawerAccAddr, err := sdk.AccAddressFromBech32(qRes.WithdrawAddress)
-	if err != nil {
-		return false, common.Address{}, err
-	}
-
-	withdrawerHexAddr := common.BytesToAddress(withdrawerAccAddr)
-	return stateDB.GetCodeSize(withdrawerHexAddr) > 0, withdrawerHexAddr, nil
+// getWithdrawerHexAddr is a helper function to get the hex address
+// of the withdrawer for the specified account address
+func (p Precompile) getWithdrawerHexAddr(ctx sdk.Context, delegatorAddr common.Address) common.Address {
+	withdrawerAccAddr := p.distributionKeeper.GetDelegatorWithdrawAddr(ctx, delegatorAddr.Bytes())
+	return common.BytesToAddress(withdrawerAccAddr)
 }
```

### precompiles/distribution/tx_test.go
```diff
@@ -447,7 +447,7 @@ func (s *PrecompileTestSuite) TestClaimRewards() {
 }
 
 func (s *PrecompileTestSuite) TestFundCommunityPool() {
-	method := s.precompile.Methods[distribution.ClaimRewardsMethod]
+	method := s.precompile.Methods[distribution.FundCommunityPoolMethod]
 
 	testCases := []struct {
 		name        string
```

### precompiles/distribution/utils_test.go
```diff
@@ -181,9 +181,9 @@ func (s *PrecompileTestSuite) DoSetupTest() {
 	s.Require().NoError(err)
 	s.precompile = precompile
 
-	coins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(5000000000000000000)))
-	inflCoins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(2000000000000000000)))
-	distrCoins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(3000000000000000000)))
+	coins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(5_000_000_000_000_000_000)))
+	inflCoins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(2_000_000_000_000_000_000)))
+	distrCoins := sdk.NewCoins(sdk.NewCoin(utils.BaseDenom, math.NewInt(3_000_000_000_000_000_000)))
 	err = s.app.BankKeeper.MintCoins(s.ctx, inflationtypes.ModuleName, coins)
 	s.Require().NoError(err)
 	err = s.app.BankKeeper.SendCoinsFromModuleToModule(s.ctx, inflationtypes.ModuleName, authtypes.FeeCollectorName, inflCoins)
```
