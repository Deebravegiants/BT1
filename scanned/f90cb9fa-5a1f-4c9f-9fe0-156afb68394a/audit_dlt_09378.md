# [?] fix(state-transition): Correctly enforce deposits length to avoid panics (#2369)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2025-01-18
Source: https://github.com/berachain/beacon-kit/commit/7b024118d781a3c8085e7dabf6fb3211be0ebb29
Type: security-commit

## Details
fix(state-transition): Correctly enforce deposits length to avoid panics (#2369)

Co-authored-by: aBear <abear@berachain.com>

## Patch
### state-transition/core/state_processor_staking.go
```diff
@@ -33,17 +33,14 @@ import (
 	"github.com/berachain/beacon-kit/state-transition/core/state"
 )
 
-// processOperations processes the operations and ensures they match the
-// local state.
+// processOperations processes the operations and ensures they match the local state.
 func (sp *StateProcessor[_]) processOperations(
 	ctx context.Context, st *state.StateDB, blk *ctypes.BeaconBlock,
 ) error {
-	// Verify that outstanding deposits are processed
-	// up to the maximum number of deposits
-
-	// Unlike Eth 2.0 specs we don't check that
-	// len(body.deposits) ==  min(MAX_DEPOSITS,
-	// state.eth1_data.deposit_count - state.eth1_deposit_index)
+	// Verify that outstanding deposits are processed up to the maximum number of deposits.
+	//
+	// Unlike Eth 2.0 specs we don't check the following:
+	// `len(body.deposits) ==  min(MAX_DEPOSITS, state.eth1_data.deposit_count - state.eth1_deposit_index)`.
 	// Instead we directly compare block deposits with store ones.
 	deposits := blk.GetBody().GetDeposits()
 	if uint64(len(deposits)) > sp.cs.MaxDepositsPerBlock() {
@@ -52,16 +49,19 @@ func (sp *StateProcessor[_]) processOperations(
 			sp.cs.MaxDepositsPerBlock(), len(deposits),
 		)
 	}
+
 	if err := sp.validateNonGenesisDeposits(
 		ctx, st, deposits, blk.GetBody().GetEth1Data().DepositRoot,
 	); err != nil {
 		return err
 	}
+
 	for _, dep := range deposits {
 		if err := sp.processDeposit(st, dep); err != nil {
 			return err
 		}
 	}
+
 	return st.SetEth1Data(blk.GetBody().Eth1Data)
 }
 
```

### state-transition/core/validation_deposits.go
```diff
@@ -78,13 +78,21 @@ func (sp *StateProcessor[_]) validateNonGenesisDeposits(
 		return err
 	}
 
-	var localDeposits ctypes.Deposits
-	localDeposits, err = sp.ds.GetDepositsByIndex(ctx, 0, depositIndex+uint64(len(blkDeposits)))
+	expectedLocalDepositsLen := depositIndex + uint64(len(blkDeposits))
+	localDeposits, err := sp.ds.GetDepositsByIndex(ctx, 0, expectedLocalDepositsLen)
 	if err != nil {
 		return err
 	}
 
-	// First check that the block's deposits 1) have contiguous indices and 2) match the local
+	// First verify that the local store returned all the expected deposits
+	if uint64(len(localDeposits)) != expectedLocalDepositsLen {
+		return errors.Wrapf(ErrDepositsLengthMismatch,
+			"local deposit count: %d, expected deposit count: %d",
+			len(localDeposits), expectedLocalDepositsLen,
+		)
+	}
+
+	// Then check that the block's deposits 1) have contiguous indices and 2) match the local
 	// view of the block's deposits.
 	for i, blkDeposit := range blkDeposits {
 		blkDepositIndex := blkDeposit.GetIndex().Unwrap()
@@ -103,7 +111,7 @@ func (sp *StateProcessor[_]) validateNonGenesisDeposits(
 		}
 	}
 
-	// Then check that the historical deposits root matches locally what's on the beacon block.
+	// Finally check that the historical deposits root matches locally what's on the beacon block.
 	if !localDeposits.HashTreeRoot().Equals(blkDepositRoot) {
 		return ErrDepositsRootMismatch
 	}
```

### state-transition/core/validation_deposits_test.go
```diff
@@ -23,6 +23,8 @@ package core_test
 import (
 	"testing"
 
+	"github.com/berachain/beacon-kit/chain"
+	"github.com/berachain/beacon-kit/config/spec"
 	"github.com/berachain/beacon-kit/consensus-types/types"
 	engineprimitives "github.com/berachain/beacon-kit/engine-primitives/engine-primitives"
 	"github.com/berachain/beacon-kit/node-core/components"
@@ -39,9 +41,7 @@ func TestInvalidDeposits(t *testing.T) {
 	var (
 		minBalance   = math.Gwei(cs.EjectionBalance() + cs.EffectiveBalanceIncrement())
 		maxBalance   = math.Gwei(cs.MaxEffectiveBalance())
-		credentials0 = types.NewCredentialsFromExecutionAddress(
-			common.ExecutionAddress{},
-		)
+		credentials0 = types.NewCredentialsFromExecutionAddress(common.ExecutionAddress{})
 	)
 
 	// Setup initial state with one validator
@@ -107,3 +107,232 @@ func TestInvalidDeposits(t *testing.T) {
 	require.Error(t, err)
 	require.ErrorContains(t, err, "deposit mismatched")
 }
+
+func TestInvalidDepositsCount(t *testing.T) {
+	cs := setupChain(t, components.BoonetChainSpecType)
+	sp, st, ds, ctx := setupState(t, cs)
+
+	var (
+		maxBalance   = math.Gwei(cs.MaxEffectiveBalance())
+		credentials0 = types.NewCredentialsFromExecutionAddress(common.ExecutionAddress{})
+	)
+
+	// Setup initial state with one validator
+	var (
+		genDeposits = types.Deposits{
+			{
+				Pubkey:      [48]byte{0x00},
+				Credentials: credentials0,
+				Amount:      maxBalance,
+				Index:       0,
+			},
+		}
+		genPayloadHeader = new(types.ExecutionPayloadHeader).Empty()
+		genVersion       = version.FromUint32[common.Version](version.Deneb)
+	)
+	require.NoError(t, ds.EnqueueDeposits(ctx, genDeposits))
+	_, err := sp.InitializePreminedBeaconStateFromEth1(
+		st, genDeposits, genPayloadHeader, genVersion,
+	)
+	require.NoError(t, err)
+
+	// Create the correct deposits.
+	correctDeposits := types.Deposits{
+		{
+			Pubkey:      [48]byte{0x01},
+			Credentials: credentials0,
+			Amount:      maxBalance,
+			Index:       1,
+		},
+		{
+			Pubkey:      [48]byte{0x02},
+			Credentials: credentials0,
+			Amount:      maxBalance,
+			Index:       2,
+		},
+	}
+
+	// Create test block with the correct deposits.
+	depRoot := append(genDeposits, correctDeposits...).HashTreeRoot()
+	blk := buildNextBlock(
+		t,
+		st,
+		&types.BeaconBlockBody{
+			ExecutionPayload: &types.ExecutionPayload{
+				Timestamp:    10,
+				ExtraData:    []byte("testing"),
+				Transactions: [][]byte{},
+				Withdrawals: []*engineprimitives.Withdrawal{
+					st.EVMInflationWithdrawal(),
+				},
+				BaseFeePerGas: math.NewU256(0),
+			},
+			Eth1Data: types.NewEth1Data(depRoot),
+			Deposits: correctDeposits,
+		},
+	)
+
+	// Add JUST 1 correct deposit to local store. This node SHOULD fail to verify.
+	require.NoError(t, ds.EnqueueDeposits(ctx, types.Deposits{correctDeposits[0]}))
+
+	// Run transition.
+	_, err = sp.Transition(ctx, st, blk)
+	require.Error(t, err)
+	require.ErrorContains(t, err, "deposits lengths mismatched")
+}
+
+func TestLocalDepositsExceedBlockDeposits(t *testing.T) {
+	csData := spec.BaseSpec()
+	csData.DepositEth1ChainID = spec.BoonetEth1ChainID
+	csData.MaxDepositsPerBlock = 1 // Set only 1 deposit allowed per block.
+	cs, err := chain.NewSpec(csData)
+	require.NoError(t, err)
+	sp, st, ds, ctx := setupState(t, cs)
+
+	var (
+		maxBalance   = math.Gwei(cs.MaxEffectiveBalance())
+		credentials0 = types.NewCredentialsFromExecutionAddress(common.ExecutionAddress{})
+	)
+
+	// Setup initial state with one validator
+	var (
+		genDeposits = types.Deposits{
+			{
+				Pubkey:      [48]byte{0x00},
+				Credentials: credentials0,
+				Amount:      maxBalance,
+				Index:       0,
+			},
+		}
+		genPayloadHeader = new(types.ExecutionPayloadHeader).Empty()
+		genVersion       = version.FromUint32[common.Version](version.Deneb)
+	)
+	require.NoError(t, ds.EnqueueDeposits(ctx, genDeposits))
+	_, err = sp.InitializePreminedBeaconStateFromEth1(
+		st, genDeposits, genPayloadHeader, genVersion,
+	)
+	require.NoError(t, err)
+
+	// Create the block deposits.
+	blockDeposits := types.Deposits{
+		{
+			Pubkey:      [48]byte{0x01},
+			Credentials: credentials0,
+			Amount:      maxBalance,
+			Index:       1,
+		},
+	}
+
+	// Create test block with the correct deposits.
+	depRoot := append(genDeposits, blockDeposits...).HashTreeRoot()
+	blk := buildNextBlock(
+		t,
+		st,
+		&types.BeaconBlockBody{
+			ExecutionPayload: &types.ExecutionPayload{
+				Timestamp:    10,
+				ExtraData:    []byte("testing"),
+				Transactions: [][]byte{},
+				Withdrawals: []*engineprimitives.Withdrawal{
+					st.EVMInflationWithdrawal(),
+				},
+				BaseFeePerGas: math.NewU256(0),
+			},
+			Eth1Data: types.NewEth1Data(depRoot),
+			Deposits: blockDeposits,
+		},
+	)
+
+	extraLocalDeposit := &types.Deposit{
+		Pubkey:      [48]byte{0x01},
+		Credentials: credentials0,
+		Amount:      maxBalance,
+		Index:       2,
+	}
+
+	// Add both deposits to local store (which includes more than what's in the block).
+	require.NoError(t, ds.EnqueueDeposits(ctx, append(blockDeposits, extraLocalDeposit)))
+
+	// Run transition.
+	_, err = sp.Transition(ctx, st, blk)
+	require.NoError(t, err)
+}
+
+func TestLocalDepositsExceedBlockDepositsBadRoot(t *testing.T) {
+	csData := spec.BaseSpec()
+	csData.DepositEth1ChainID = spec.BoonetEth1ChainID
+	csData.MaxDepositsPerBlock = 1 // Set only 1 deposit allowed per block.
+	cs, err := chain.NewSpec(csData)
+	require.NoError(t, err)
+	sp, st, ds, ctx := setupState(t, cs)
+
+	var (
+		maxBalance   = math.Gwei(cs.MaxEffectiveBalance())
+		credentials0 = types.NewCredentialsFromExecutionAddress(common.ExecutionAddress{})
+	)
+
+	// Setup initial state with one validator
+	var (
+		genDeposits = types.Deposits{
+			{
+				Pubkey:      [48]byte{0x00},
+				Credentials: credentials0,
+				Amount:      maxBalance,
+				Index:       0,
+			},
+		}
+		genPayloadHeader = new(types.ExecutionPayloadHeader).Empty()
+		genVersion       = version.FromUint32[common.Version](version.Deneb)
+	)
+	require.NoError(t, ds.EnqueueDeposits(ctx, genDeposits))
+	_, err = sp.InitializePreminedBeaconStateFromEth1(
+		st, genDeposits, genPayloadHeader, genVersion,
+	)
+	require.NoError(t, err)
+
+	// Create the block deposits.
+	blockDeposits := types.Deposits{
+		{
+			Pubkey:      [48]byte{0x01},
+			Credentials: credentials0,
+			Amount:      maxBalance,
+			Index:       1,
+		},
+	}
+
+	extraLocalDeposit := &types.Deposit{
+		Pubkey:      [48]byte{0x01},
+		Credentials: credentials0,
+		Amount:      maxBalance,
+		Index:       2,
+	}
+
+	// Now, the block proposer ends up adding the correct 1 deposit per block, BUT spoofs the
+	// deposits root to use the entire deposits list.
+	badDepRoot := append(genDeposits, append(blockDeposits, extraLocalDeposit)...).HashTreeRoot()
+	blk := buildNextBlock(
+		t,
+		st,
+		&types.BeaconBlockBody{
+			ExecutionPayload: &types.ExecutionPayload{
+				Timestamp:    10,
+				ExtraData:    []byte("testing"),
+				Transactions: [][]byte{},
+				Withdrawals: []*engineprimitives.Withdrawal{
+					st.EVMInflationWithdrawal(),
+				},
+				BaseFeePerGas: math.NewU256(0),
+			},
+			Eth1Data: types.NewEth1Data(badDepRoot),
+			Deposits: blockDeposits,
+		},
+	)
+
+	// Add both deposits to local store (which includes more than what's in the block).
+	require.NoError(t, ds.EnqueueDeposits(ctx, append(blockDeposits, extraLocalDeposit)))
+
+	// Run transition.
+	_, err = sp.Transition(ctx, st, blk)
+	require.Error(t, err)
+	require.ErrorContains(t, err, "deposits root mismatch")
+}
```
