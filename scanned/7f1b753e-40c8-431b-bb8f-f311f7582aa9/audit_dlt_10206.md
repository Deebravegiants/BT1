# [?] go/consensus/tendermint: Fix nil deref in EstimateGas

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-01-23
Source: https://github.com/oasisprotocol/oasis-core/commit/f23b6cbf48109a1c7605d30771b9ba3abf17a873
Type: security-commit

## Details
go/consensus/tendermint: Fix nil deref in EstimateGas

## Patch
### .changelog/3648.bugfix.md
```diff
@@ -0,0 +1 @@
+go/consensus/tendermint: Fix nil deref in EstimateGas
```

### go/consensus/api/api.go
```diff
@@ -54,6 +54,9 @@ var (
 
 	// ErrDuplicateTx is the error returned when the transaction already exists in the mempool.
 	ErrDuplicateTx = errors.New(moduleName, 5, "consensus: duplicate transaction")
+
+	// ErrInvalidArgument is the error returned when the request contains an invalid argument.
+	ErrInvalidArgument = errors.New(moduleName, 6, "consensus: invalid argument")
 )
 
 // FeatureMask is the consensus backend feature bitmask.
```

### go/consensus/tendermint/abci/mux.go
```diff
@@ -573,6 +573,10 @@ func (mux *abciMux) executeTx(ctx *api.Context, rawTx []byte) error {
 }
 
 func (mux *abciMux) EstimateGas(caller signature.PublicKey, tx *transaction.Transaction) (transaction.Gas, error) {
+	if tx == nil {
+		return 0, consensus.ErrInvalidArgument
+	}
+
 	// As opposed to other transaction dispatch entry points (CheckTx/DeliverTx), this method can
 	// be called in parallel to the consensus layer and to other invocations.
 	//
```

### go/consensus/tests/tester.go
```diff
@@ -94,6 +94,9 @@ func ConsensusImplementationTests(t *testing.T, backend consensus.ClientBackend)
 	require.NoError(err, "GetEpoch")
 	require.True(epoch > 0, "epoch height should be greater than zero")
 
+	_, err = backend.EstimateGas(ctx, &consensus.EstimateGasRequest{})
+	require.ErrorIs(err, consensus.ErrInvalidArgument, "EstimateGas with nil transaction should fail")
+
 	_, err = backend.EstimateGas(ctx, &consensus.EstimateGasRequest{
 		Signer:      memorySigner.NewTestSigner("estimate gas signer").Public(),
 		Transaction: transaction.NewTransaction(0, nil, staking.MethodTransfer, &staking.Transfer{}),
```
