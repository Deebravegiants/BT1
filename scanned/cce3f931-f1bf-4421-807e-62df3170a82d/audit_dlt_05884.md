# [?] fix: estimateFee panic w/ missing required fields (#2770)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-04-18
Source: https://github.com/NethermindEth/juno/commit/8880dcd0e8d90cda359ab03e48fb4e0fb1e7b7f7
Type: security-commit

## Details
fix: estimateFee panic w/ missing required fields (#2770)

* fix: estimateFee panic w/ missing required fields

Closes #2475

This PR fixes the issue by doing the following:

1. Adding checks for the fields at `prepareTransactions`
2. Using a struct for `ResourceBounds` instead of the map, which
   enforces the required fields when `ResourceBounds` is provided.

The change of using a struct for the `ResourceBounds` does mean that
there is a need to manually copy over the values since copy does not
convert the rpc `ResourceBounds` to core `ResourceBound` automatically.

When fixing the issue, also found several concerning points:

1. Since `omitempty` takes precedence over the `validate` tag, is there
   some other fields currently/in the future that might cause the same issue?
2. Since this bug exists for all version of rpc, maintaining multiple
   rpc directory might not be a good idea, maybe there's a method to
better consolidate the different rpc versions?

* refactor: reuse rpc types & clean up comparisons

## Patch
### rpc/v6/block_test.go
```diff
@@ -550,12 +550,12 @@ func TestBlockWithTxHashesV013(t *testing.T) {
 				Signature:          &tx.TransactionSignature,
 				CallData:           &tx.CallData,
 				EntryPointSelector: tx.EntryPointSelector,
-				ResourceBounds: &map[rpc.Resource]rpc.ResourceBounds{
-					rpc.ResourceL1Gas: {
+				ResourceBounds: &rpc.ResourceBoundsMap{
+					L1Gas: &rpc.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL1Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL1Gas].MaxPricePerUnit,
 					},
-					rpc.ResourceL2Gas: {
+					L2Gas: &rpc.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL2Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL2Gas].MaxPricePerUnit,
 					},
```

### rpc/v6/simulation.go
```diff
@@ -12,6 +12,7 @@ import (
 	rpccore "github.com/NethermindEth/juno/rpc/rpccore"
 	"github.com/NethermindEth/juno/utils"
 	"github.com/NethermindEth/juno/vm"
+	"github.com/crate-crypto/go-ipa/bandersnatch/fp"
 )
 
 type SimulationFlag int
@@ -21,6 +22,15 @@ const (
 	SkipFeeChargeFlag
 )
 
+var RPCVersion3Value = felt.Felt(fp.Element(
+	[4]uint64{
+		18446744073709551521,
+		18446744073709551615,
+		18446744073709551615,
+		576460752303421872,
+	},
+))
+
 func (s *SimulationFlag) UnmarshalJSON(bytes []byte) (err error) {
 	switch flag := string(bytes); flag {
 	case `"SKIP_VALIDATE"`:
@@ -101,6 +111,25 @@ func (h *Handler) simulateTransactions(id BlockID, transactions []BroadcastedTra
 	return simulatedTransactions, nil
 }
 
+func IsVersion3(version *felt.Felt) bool {
+	return version != nil && version.Equal(&RPCVersion3Value)
+}
+
+func checkTxHasSenderAddress(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnDeclare ||
+		tx.Transaction.Type == TxnInvoke) &&
+		IsVersion3(tx.Version) &&
+		tx.Transaction.SenderAddress == nil
+}
+
+func checkTxHasResourceBounds(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnInvoke ||
+		tx.Transaction.Type == TxnDeployAccount ||
+		tx.Transaction.Type == TxnDeclare) &&
+		IsVersion3(tx.Version) &&
+		tx.Transaction.ResourceBounds == nil
+}
+
 func prepareTransactions(transactions []BroadcastedTransaction, network *utils.Network) (
 	[]core.Transaction, []core.Class, []*felt.Felt, *jsonrpc.Error,
 ) {
@@ -109,6 +138,20 @@ func prepareTransactions(transactions []BroadcastedTransaction, network *utils.N
 	paidFeesOnL1 := make([]*felt.Felt, 0)
 
 	for idx := range transactions {
+		// Check for missing required fields in struct that can't be validated by
+		// jsonschema due to validation happening after omit empty
+		//
+		// TODO: as its expected that this will happen in other cases as well,
+		// it might be a good idea to implement a custom validator and unmarshal handler
+		// to solve this problem in a more elegant way
+		if checkTxHasSenderAddress(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type")
+		}
+
+		if checkTxHasResourceBounds(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type")
+		}
+
 		txn, declaredClass, paidFeeOnL1, aErr := AdaptBroadcastedTransaction(&transactions[idx], network)
 		if aErr != nil {
 			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, aErr.Error())
```

### rpc/v6/simulation_test.go
```diff
@@ -7,6 +7,7 @@ import (
 
 	"github.com/NethermindEth/juno/core"
 	"github.com/NethermindEth/juno/core/felt"
+	"github.com/NethermindEth/juno/jsonrpc"
 	"github.com/NethermindEth/juno/mocks"
 	rpccore "github.com/NethermindEth/juno/rpc/rpccore"
 	rpc "github.com/NethermindEth/juno/rpc/v6"
@@ -115,3 +116,122 @@ func TestSimulateTransactions(t *testing.T) {
 		)), err)
 	})
 }
+
+func TestSimulateTransactionsShouldErrorWithoutSenderAddressOrResourceBounds(t *testing.T) {
+	t.Parallel()
+	n := &utils.Mainnet
+	headsHeader := &core.Header{
+		SequencerAddress: n.BlockHashMetaInfo.FallBackSequencerAddress,
+		L1GasPriceETH:    &felt.Zero,
+		L1GasPriceSTRK:   &felt.Zero,
+		L1DAMode:         0,
+		L1DataGasPrice: &core.GasPrice{
+			PriceInWei: &felt.Zero,
+			PriceInFri: &felt.Zero,
+		},
+		L2GasPrice: &core.GasPrice{
+			PriceInWei: &felt.Zero,
+			PriceInFri: &felt.Zero,
+		},
+	}
+
+	version3 := felt.FromUint64(3)
+
+	tests := []struct {
+		name         string
+		transactions []rpc.BroadcastedTransaction
+		err          *jsonrpc.Error
+	}{
+		{
+			name: "declare transaction without sender address",
+			transactions: []rpc.BroadcastedTransaction{
+				{
+					Transaction: rpc.Transaction{
+						Version: &version3,
+						Type:    rpc.TxnDeclare,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type"),
+		},
+		{
+			name: "declare transaction without resource bounds",
+			transactions: []rpc.BroadcastedTransaction{
+				{
+					Transaction: rpc.Transaction{
+						Version:       &version3,
+						Type:          rpc.TxnDeclare,
+						SenderAddress: &felt.Zero,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+		{
+			name: "invoke transaction without sender address",
+			transactions: []rpc.BroadcastedTransaction{
+				{
+					Transaction: rpc.Transaction{
+						Version: &version3,
+						Type:    rpc.TxnInvoke,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type"),
+		},
+		{
+			name: "invoke transaction without resource bounds",
+			transactions: []rpc.BroadcastedTransaction{
+				{
+					Transaction: rpc.Transaction{
+						Version:       &version3,
+						Type:          rpc.TxnInvoke,
+						SenderAddress: &felt.Zero,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+		{
+			name: "deploy account transaction without resource bounds",
+			transactions: []rpc.BroadcastedTransaction{
+				{
+					Transaction: rpc.Transaction{
+						Version: &version3,
+						Type:    rpc.TxnDeployAccount,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+	}
+
+	for _, test := range tests {
+		t.Run(test.name, func(t *testing.T) {
+			t.Parallel()
+			mockCtrl := gomock.NewController(t)
+			defer mockCtrl.Finish()
+
+			mockReader := mocks.NewMockReader(mockCtrl)
+			mockVM := mocks.NewMockVM(mockCtrl)
+			mockState := mocks.NewMockStateHistoryReader(mockCtrl)
+
+			mockReader.EXPECT().Network().Return(n)
+			mockReader.EXPECT().HeadState().Return(mockState, nopCloser, nil)
+			mockReader.EXPECT().HeadsHeader().Return(headsHeader, nil)
+
+			handler := rpc.New(mockReader, nil, mockVM, "", n, utils.NewNopZapLogger())
+
+			_, err := handler.SimulateTransactions(
+				rpc.BlockID{Latest: true},
+				test.transactions,
+				[]rpc.SimulationFlag{},
+			)
+			if test.err != nil {
+				require.Equal(t, test.err, err)
+				return
+			}
+			require.Nil(t, err)
+		})
+	}
+}
```

### rpc/v6/transaction.go
```diff
@@ -199,30 +199,39 @@ type ResourceBounds struct {
 	MaxPricePerUnit *felt.Felt `json:"max_price_per_unit"`
 }
 
+// TODO: using Value fields here is a good idea, however
+// we are currently keeping the field's type Reference since the current
+// validation tags we are using does not work well with Value field.
+// We should revisit this when we start implementing custom validations.
+type ResourceBoundsMap struct {
+	L1Gas *ResourceBounds `json:"l1_gas" validate:"required"`
+	L2Gas *ResourceBounds `json:"l2_gas" validate:"required"`
+}
+
 // https://github.com/starkware-libs/starknet-specs/blob/a789ccc3432c57777beceaa53a34a7ae2f25fda0/api/starknet_api_openrpc.json#L1252
 //
 //nolint:lll
 type Transaction struct {
-	Hash                  *felt.Felt                   `json:"transaction_hash,omitempty"`
-	Type                  TransactionType              `json:"type" validate:"required"`
-	Version               *felt.Felt                   `json:"version,omitempty" validate:"required"`
-	Nonce                 *felt.Felt                   `json:"nonce,omitempty" validate:"required_unless=Version 0x0"`
-	MaxFee                *felt.Felt                   `json:"max_fee,omitempty" validate:"required_if=Version 0x0,required_if=Version 0x1,required_if=Version 0x2"`
-	ContractAddress       *felt.Felt                   `json:"contract_address,omitempty"`
-	ContractAddressSalt   *felt.Felt                   `json:"contract_address_salt,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	ClassHash             *felt.Felt                   `json:"class_hash,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	ConstructorCallData   *[]*felt.Felt                `json:"constructor_calldata,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	SenderAddress         *felt.Felt                   `json:"sender_address,omitempty" validate:"required_if=Type DECLARE,required_if=Type INVOKE Version 0x1,required_if=Type INVOKE Version 0x3"`
-	Signature             *[]*felt.Felt                `json:"signature,omitempty" validate:"required"`
-	CallData              *[]*felt.Felt                `json:"calldata,omitempty" validate:"required_if=Type INVOKE"`
-	EntryPointSelector    *felt.Felt                   `json:"entry_point_selector,omitempty" validate:"required_if=Type INVOKE Version 0x0"`
-	CompiledClassHash     *felt.Felt                   `json:"compiled_class_hash,omitempty" validate:"required_if=Type DECLARE Version 0x2"`
-	ResourceBounds        *map[Resource]ResourceBounds `json:"resource_bounds,omitempty" validate:"required_if=Version 0x3"`
-	Tip                   *felt.Felt                   `json:"tip,omitempty" validate:"required_if=Version 0x3"`
-	PaymasterData         *[]*felt.Felt                `json:"paymaster_data,omitempty" validate:"required_if=Version 0x3"`
-	AccountDeploymentData *[]*felt.Felt                `json:"account_deployment_data,omitempty" validate:"required_if=Type INVOKE Version 0x3,required_if=Type DECLARE Version 0x3"`
-	NonceDAMode           *DataAvailabilityMode        `json:"nonce_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
-	FeeDAMode             *DataAvailabilityMode        `json:"fee_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
+	Hash                  *felt.Felt            `json:"transaction_hash,omitempty"`
+	Type                  TransactionType       `json:"type" validate:"required"`
+	Version               *felt.Felt            `json:"version,omitempty" validate:"required"`
+	Nonce                 *felt.Felt            `json:"nonce,omitempty" validate:"required_unless=Version 0x0"`
+	MaxFee                *felt.Felt            `json:"max_fee,omitempty" validate:"required_if=Version 0x0,required_if=Version 0x1,required_if=Version 0x2"`
+	ContractAddress       *felt.Felt            `json:"contract_address,omitempty"`
+	ContractAddressSalt   *felt.Felt            `json:"contract_address_salt,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	ClassHash             *felt.Felt            `json:"class_hash,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	ConstructorCallData   *[]*felt.Felt         `json:"constructor_calldata,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	SenderAddress         *felt.Felt            `json:"sender_address,omitempty" validate:"required_if=Type DECLARE,required_if=Type INVOKE Version 0x1,required_if=Type INVOKE Version 0x3"`
+	Signature             *[]*felt.Felt         `json:"signature,omitempty" validate:"required"`
+	CallData              *[]*felt.Felt         `json:"calldata,omitempty" validate:"required_if=Type INVOKE"`
+	EntryPointSelector    *felt.Felt            `json:"entry_point_selector,omitempty" validate:"required_if=Type INVOKE Version 0x0"`
+	CompiledClassHash     *felt.Felt            `json:"compiled_class_hash,omitempty" validate:"required_if=Type DECLARE Version 0x2"`
+	ResourceBounds        *ResourceBoundsMap    `json:"resource_bounds,omitempty" validate:"required_if=Version 0x3"`
+	Tip                   *felt.Felt            `json:"tip,omitempty" validate:"required_if=Version 0x3"`
+	PaymasterData         *[]*felt.Felt         `json:"paymaster_data,omitempty" validate:"required_if=Version 0x3"`
+	AccountDeploymentData *[]*felt.Felt         `json:"account_deployment_data,omitempty" validate:"required_if=Type INVOKE Version 0x3,required_if=Type DECLARE Version 0x3"`
+	NonceDAMode           *DataAvailabilityMode `json:"nonce_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
+	FeeDAMode             *DataAvailabilityMode `json:"fee_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
 }
 
 type TransactionStatus struct {
@@ -309,18 +318,24 @@ type BroadcastedTransaction struct {
 func AdaptBroadcastedTransaction(broadcastedTxn *BroadcastedTransaction,
 	network *utils.Network,
 ) (core.Transaction, core.Class, *felt.Felt, error) {
-	// RPCv6 requests must set l2_gas to zero
-	if broadcastedTxn.ResourceBounds != nil {
-		(*broadcastedTxn.ResourceBounds)[ResourceL2Gas] = ResourceBounds{
-			MaxAmount:       new(felt.Felt).SetUint64(0),
-			MaxPricePerUnit: new(felt.Felt).SetUint64(0),
-		}
-	}
 	var feederTxn starknet.Transaction
 	if err := copier.Copy(&feederTxn, broadcastedTxn.Transaction); err != nil {
 		return nil, nil, nil, err
 	}
 
+	// RPCv6 requests must set l2_gas to zero
+	if broadcastedTxn.ResourceBounds != nil {
+		broadcastedTxn.ResourceBounds = &ResourceBoundsMap{
+			L1Gas: broadcastedTxn.ResourceBounds.L1Gas,
+			L2Gas: &ResourceBounds{
+				MaxAmount:       new(felt.Felt).SetUint64(0),
+				MaxPricePerUnit: new(felt.Felt).SetUint64(0),
+			},
+		}
+		// Copy doesn't covert the struct to enum correctly, so we need to adapt it
+		feederTxn.ResourceBounds = adaptToFeederResourceBounds(broadcastedTxn.ResourceBounds)
+	}
+
 	txn, err := sn2core.AdaptTransaction(&feederTxn)
 	if err != nil {
 		return nil, nil, nil, err
@@ -369,32 +384,32 @@ func AdaptBroadcastedTransaction(broadcastedTxn *BroadcastedTransaction,
 	return txn, declaredClass, paidFeeOnL1, nil
 }
 
-func adaptResourceBounds(rb map[core.Resource]core.ResourceBounds) map[Resource]ResourceBounds {
-	rpcResourceBounds := make(map[Resource]ResourceBounds)
-	for resource, bounds := range rb {
-		// ResourceL1DataGas is not supported in v6
-		if resource == core.ResourceL1DataGas {
-			continue
-		}
-
-		rpcResourceBounds[Resource(resource)] = ResourceBounds{
-			MaxAmount:       new(felt.Felt).SetUint64(bounds.MaxAmount),
-			MaxPricePerUnit: bounds.MaxPricePerUnit,
-		}
+func adaptResourceBounds(rb map[core.Resource]core.ResourceBounds) ResourceBoundsMap {
+	rpcResourceBounds := ResourceBoundsMap{
+		L1Gas: &ResourceBounds{
+			MaxAmount:       new(felt.Felt).SetUint64(rb[core.ResourceL1Gas].MaxAmount),
+			MaxPricePerUnit: rb[core.ResourceL1Gas].MaxPricePerUnit,
+		},
+		L2Gas: &ResourceBounds{
+			MaxAmount:       new(felt.Felt).SetUint64(rb[core.ResourceL2Gas].MaxAmount),
+			MaxPricePerUnit: rb[core.ResourceL2Gas].MaxPricePerUnit,
+		},
 	}
 	return rpcResourceBounds
 }
 
-func adaptToFeederResourceBounds(rb *map[Resource]ResourceBounds) *map[starknet.Resource]starknet.ResourceBounds { //nolint:gocritic
+func adaptToFeederResourceBounds(rb *ResourceBoundsMap) *map[starknet.Resource]starknet.ResourceBounds { //nolint:gocritic
 	if rb == nil {
 		return nil
 	}
 	feederResourceBounds := make(map[starknet.Resource]starknet.ResourceBounds)
-	for resource, bounds := range *rb {
-		feederResourceBounds[starknet.Resource(resource)] = starknet.ResourceBounds{
-			MaxAmount:       bounds.MaxAmount,
-			MaxPricePerUnit: bounds.MaxPricePerUnit,
-		}
+	feederResourceBounds[starknet.ResourceL1Gas] = starknet.ResourceBounds{
+		MaxAmount:       rb.L1Gas.MaxAmount,
+		MaxPricePerUnit: rb.L1Gas.MaxPricePerUnit,
+	}
+	feederResourceBounds[starknet.ResourceL2Gas] = starknet.ResourceBounds{
+		MaxAmount:       rb.L2Gas.MaxAmount,
+		MaxPricePerUnit: rb.L2Gas.MaxPricePerUnit,
 	}
 	return &feederResourceBounds
 }
```

### rpc/v6/transaction_test.go
```diff
@@ -1138,9 +1138,9 @@ func TestAdaptTransaction(t *testing.T) {
 		expectedTx := &rpc.Transaction{
 			Type:    rpc.TxnInvoke,
 			Version: new(felt.Felt).SetUint64(3),
-			ResourceBounds: &map[rpc.Resource]rpc.ResourceBounds{
-				rpc.ResourceL1Gas: {MaxAmount: new(felt.Felt).SetUint64(1), MaxPricePerUnit: new(felt.Felt).SetUint64(2)},
-				rpc.ResourceL2Gas: {MaxAmount: new(felt.Felt).SetUint64(3), MaxPricePerUnit: new(felt.Felt).SetUint64(4)},
+			ResourceBounds: &rpc.ResourceBoundsMap{
+				L1Gas: &rpc.ResourceBounds{MaxAmount: new(felt.Felt).SetUint64(1), MaxPricePerUnit: new(felt.Felt).SetUint64(2)},
+				L2Gas: &rpc.ResourceBounds{MaxAmount: new(felt.Felt).SetUint64(3), MaxPricePerUnit: new(felt.Felt).SetUint64(4)},
 			},
 			Tip: new(felt.Felt).SetUint64(0),
 			// Those 4 fields are pointers to slice (the SliceHeader is allocated, it just refers to a nil array)
```

### rpc/v7/block_test.go
```diff
@@ -422,12 +422,12 @@ func TestBlockWithTxHashesV013(t *testing.T) {
 				Signature:          &tx.TransactionSignature,
 				CallData:           &tx.CallData,
 				EntryPointSelector: tx.EntryPointSelector,
-				ResourceBounds: &map[rpcv7.Resource]rpcv7.ResourceBounds{
-					rpcv7.ResourceL1Gas: {
+				ResourceBounds: &rpcv6.ResourceBoundsMap{
+					L1Gas: &rpcv6.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL1Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL1Gas].MaxPricePerUnit,
 					},
-					rpcv7.ResourceL2Gas: {
+					L2Gas: &rpcv6.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL2Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL2Gas].MaxPricePerUnit,
 					},
```

### rpc/v7/simulation.go
```diff
@@ -93,6 +93,21 @@ func (h *Handler) simulateTransactions(id BlockID, transactions []BroadcastedTra
 	return simulatedTransactions, httpHeader, nil
 }
 
+func checkTxHasSenderAddress(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnDeclare ||
+		tx.Transaction.Type == TxnInvoke) &&
+		rpcv6.IsVersion3(tx.Version) &&
+		tx.Transaction.SenderAddress == nil
+}
+
+func checkTxHasResourceBounds(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnInvoke ||
+		tx.Transaction.Type == TxnDeployAccount ||
+		tx.Transaction.Type == TxnDeclare) &&
+		rpcv6.IsVersion3(tx.Version) &&
+		tx.Transaction.ResourceBounds == nil
+}
+
 func prepareTransactions(transactions []BroadcastedTransaction, network *utils.Network) (
 	[]core.Transaction, []core.Class, []*felt.Felt, *jsonrpc.Error,
 ) {
@@ -101,6 +116,20 @@ func prepareTransactions(transactions []BroadcastedTransaction, network *utils.N
 	paidFeesOnL1 := make([]*felt.Felt, 0)
 
 	for idx := range transactions {
+		// Check for missing required fields in struct that can't be validated by
+		// jsonschema due to validation happening after omit empty
+		//
+		// TODO: as its expected that this will happen in other cases as well,
+		// it might be a good idea to implement a custom validator and unmarshal handler
+		// to solve this problem in a more elegant way
+		if checkTxHasSenderAddress(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type")
+		}
+
+		if checkTxHasResourceBounds(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type")
+		}
+
 		txn, declaredClass, paidFeeOnL1, aErr := AdaptBroadcastedTransaction(&transactions[idx], network)
 		if aErr != nil {
 			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, aErr.Error())
```

### rpc/v7/simulation_test.go
```diff
@@ -7,6 +7,7 @@ import (
 
 	"github.com/NethermindEth/juno/core"
 	"github.com/NethermindEth/juno/core/felt"
+	"github.com/NethermindEth/juno/jsonrpc"
 	"github.com/NethermindEth/juno/mocks"
 	"github.com/NethermindEth/juno/rpc/rpccore"
 	rpcv6 "github.com/NethermindEth/juno/rpc/v6"
@@ -109,3 +110,122 @@ func TestSimulateTransactions(t *testing.T) {
 		require.Equal(t, httpHeader.Get(rpcv7.ExecutionStepsHeader), "0")
 	})
 }
+
+func TestSimulateTransactionsShouldErrorWithoutSenderAddressOrResourceBounds(t *testing.T) {
+	t.Parallel()
+	n := &utils.Mainnet
+	headsHeader := &core.Header{
+		SequencerAddress: n.BlockHashMetaInfo.FallBackSequencerAddress,
+		L1GasPriceETH:    &felt.Zero,
+		L1GasPriceSTRK:   &felt.Zero,
+		L1DAMode:         0,
+		L1DataGasPrice: &core.GasPrice{
+			PriceInWei: &felt.Zero,
+			PriceInFri: &felt.Zero,
+		},
+		L2GasPrice: &core.GasPrice{
+			PriceInWei: &felt.Zero,
+			PriceInFri: &felt.Zero,
+		},
+	}
+
+	version3 := felt.FromUint64(3)
+
+	tests := []struct {
+		name         string
+		transactions []rpcv7.BroadcastedTransaction
+		err          *jsonrpc.Error
+	}{
+		{
+			name: "declare transaction without sender address",
+			transactions: []rpcv7.BroadcastedTransaction{
+				{
+					Transaction: rpcv7.Transaction{
+						Version: &version3,
+						Type:    rpcv7.TxnDeclare,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type"),
+		},
+		{
+			name: "declare transaction without resource bounds",
+			transactions: []rpcv7.BroadcastedTransaction{
+				{
+					Transaction: rpcv7.Transaction{
+						Version:       &version3,
+						Type:          rpcv7.TxnDeclare,
+						SenderAddress: &felt.Zero,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+		{
+			name: "invoke transaction without sender address",
+			transactions: []rpcv7.BroadcastedTransaction{
+				{
+					Transaction: rpcv7.Transaction{
+						Version: &version3,
+						Type:    rpcv7.TxnInvoke,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type"),
+		},
+		{
+			name: "invoke transaction without resource bounds",
+			transactions: []rpcv7.BroadcastedTransaction{
+				{
+					Transaction: rpcv7.Transaction{
+						Version:       &version3,
+						Type:          rpcv7.TxnInvoke,
+						SenderAddress: &felt.Zero,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+		{
+			name: "deploy account transaction without resource bounds",
+			transactions: []rpcv7.BroadcastedTransaction{
+				{
+					Transaction: rpcv7.Transaction{
+						Version: &version3,
+						Type:    rpcv7.TxnDeployAccount,
+					},
+				},
+			},
+			err: jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type"),
+		},
+	}
+
+	for _, test := range tests {
+		t.Run(test.name, func(t *testing.T) {
+			t.Parallel()
+			mockCtrl := gomock.NewController(t)
+			defer mockCtrl.Finish()
+
+			mockReader := mocks.NewMockReader(mockCtrl)
+			mockVM := mocks.NewMockVM(mockCtrl)
+			mockState := mocks.NewMockStateHistoryReader(mockCtrl)
+
+			mockReader.EXPECT().Network().Return(n)
+			mockReader.EXPECT().HeadState().Return(mockState, nopCloser, nil)
+			mockReader.EXPECT().HeadsHeader().Return(headsHeader, nil)
+
+			handler := rpcv7.New(mockReader, nil, mockVM, "", n, utils.NewNopZapLogger())
+
+			_, _, err := handler.SimulateTransactions(
+				rpcv7.BlockID{Latest: true},
+				test.transactions,
+				[]rpcv6.SimulationFlag{},
+			)
+			if test.err != nil {
+				require.Equal(t, test.err, err)
+				return
+			}
+			require.Nil(t, err)
+		})
+	}
+}
```

### rpc/v7/transaction.go
```diff
@@ -13,6 +13,7 @@ import (
 	"github.com/NethermindEth/juno/db"
 	"github.com/NethermindEth/juno/jsonrpc"
 	"github.com/NethermindEth/juno/rpc/rpccore"
+	rpcv6 "github.com/NethermindEth/juno/rpc/v6"
 	"github.com/NethermindEth/juno/starknet"
 	"github.com/NethermindEth/juno/utils"
 	"github.com/ethereum/go-ethereum/common"
@@ -159,69 +160,30 @@ func (m *DataAvailabilityMode) UnmarshalJSON(data []byte) error {
 	return nil
 }
 
-type Resource uint32
-
-const (
-	ResourceL1Gas Resource = iota + 1
-	ResourceL2Gas
-)
-
-func (r Resource) MarshalText() ([]byte, error) {
-	switch r {
-	case ResourceL1Gas:
-		return []byte("l1_gas"), nil
-	case ResourceL2Gas:
-		return []byte("l2_gas"), nil
-	default:
-		return nil, fmt.Errorf("unknown Resource %v", r)
-	}
-}
-
-func (r *Resource) UnmarshalJSON(data []byte) error {
-	switch string(data) {
-	case `"l1_gas"`:
-		*r = ResourceL1Gas
-	case `"l2_gas"`:
-		*r = ResourceL2Gas
-	default:
-		return fmt.Errorf("unknown Resource: %q", string(data))
-	}
-	return nil
-}
-
-func (r *Resource) UnmarshalText(data []byte) error {
-	return r.UnmarshalJSON(data)
-}
-
-type ResourceBounds struct {
-	MaxAmount       *felt.Felt `json:"max_amount"`
-	MaxPricePerUnit *felt.Felt `json:"max_price_per_unit"`
-}
-
 // https://github.com/starkware-libs/starknet-specs/blob/a789ccc3432c57777beceaa53a34a7ae2f25fda0/api/starknet_api_openrpc.json#L1252
 //
 //nolint:lll
 type Transaction struct {
-	Hash                  *felt.Felt                   `json:"transaction_hash,omitempty"`
-	Type                  TransactionType              `json:"type" validate:"required"`
-	Version               *felt.Felt                   `json:"version,omitempty" validate:"required"`
-	Nonce                 *felt.Felt                   `json:"nonce,omitempty" validate:"required_unless=Version 0x0"`
-	MaxFee                *felt.Felt                   `json:"max_fee,omitempty" validate:"required_if=Version 0x0,required_if=Version 0x1,required_if=Version 0x2"`
-	ContractAddress       *felt.Felt                   `json:"contract_address,omitempty"`
-	ContractAddressSalt   *felt.Felt                   `json:"contract_address_salt,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	ClassHash             *felt.Felt                   `json:"class_hash,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	ConstructorCallData   *[]*felt.Felt                `json:"constructor_calldata,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
-	SenderAddress         *felt.Felt                   `json:"sender_address,omitempty" validate:"required_if=Type DECLARE,required_if=Type INVOKE Version 0x1,required_if=Type INVOKE Version 0x3"`
-	Signature             *[]*felt.Felt                `json:"signature,omitempty" validate:"required"`
-	CallData              *[]*felt.Felt                `json:"calldata,omitempty" validate:"required_if=Type INVOKE"`
-	EntryPointSelector    *felt.Felt                   `json:"entry_point_selector,omitempty" validate:"required_if=Type INVOKE Version 0x0"`
-	CompiledClassHash     *felt.Felt                   `json:"compiled_class_hash,omitempty" validate:"required_if=Type DECLARE Version 0x2"`
-	ResourceBounds        *map[Resource]ResourceBounds `json:"resource_bounds,omitempty" validate:"required_if=Version 0x3"`
-	Tip                   *felt.Felt                   `json:"tip,omitempty" validate:"required_if=Version 0x3"`
-	PaymasterData         *[]*felt.Felt                `json:"paymaster_data,omitempty" validate:"required_if=Version 0x3"`
-	AccountDeploymentData *[]*felt.Felt                `json:"account_deployment_data,omitempty" validate:"required_if=Type INVOKE Version 0x3,required_if=Type DECLARE Version 0x3"`
-	NonceDAMode           *DataAvailabilityMode        `json:"nonce_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
-	FeeDAMode             *DataAvailabilityMode        `json:"fee_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
+	Hash                  *felt.Felt               `json:"transaction_hash,omitempty"`
+	Type                  TransactionType          `json:"type" validate:"required"`
+	Version               *felt.Felt               `json:"version,omitempty" validate:"required"`
+	Nonce                 *felt.Felt               `json:"nonce,omitempty" validate:"required_unless=Version 0x0"`
+	MaxFee                *felt.Felt               `json:"max_fee,omitempty" validate:"required_if=Version 0x0,required_if=Version 0x1,required_if=Version 0x2"`
+	ContractAddress       *felt.Felt               `json:"contract_address,omitempty"`
+	ContractAddressSalt   *felt.Felt               `json:"contract_address_salt,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	ClassHash             *felt.Felt               `json:"class_hash,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	ConstructorCallData   *[]*felt.Felt            `json:"constructor_calldata,omitempty" validate:"required_if=Type DEPLOY,required_if=Type DEPLOY_ACCOUNT"`
+	SenderAddress         *felt.Felt               `json:"sender_address,omitempty" validate:"required_if=Type DECLARE,required_if=Type INVOKE Version 0x1,required_if=Type INVOKE Version 0x3"`
+	Signature             *[]*felt.Felt            `json:"signature,omitempty" validate:"required"`
+	CallData              *[]*felt.Felt            `json:"calldata,omitempty" validate:"required_if=Type INVOKE"`
+	EntryPointSelector    *felt.Felt               `json:"entry_point_selector,omitempty" validate:"required_if=Type INVOKE Version 0x0"`
+	CompiledClassHash     *felt.Felt               `json:"compiled_class_hash,omitempty" validate:"required_if=Type DECLARE Version 0x2"`
+	ResourceBounds        *rpcv6.ResourceBoundsMap `json:"resource_bounds,omitempty" validate:"required_if=Version 0x3"`
+	Tip                   *felt.Felt               `json:"tip,omitempty" validate:"required_if=Version 0x3"`
+	PaymasterData         *[]*felt.Felt            `json:"paymaster_data,omitempty" validate:"required_if=Version 0x3"`
+	AccountDeploymentData *[]*felt.Felt            `json:"account_deployment_data,omitempty" validate:"required_if=Type INVOKE Version 0x3,required_if=Type DECLARE Version 0x3"`
+	NonceDAMode           *DataAvailabilityMode    `json:"nonce_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
+	FeeDAMode             *DataAvailabilityMode    `json:"fee_data_availability_mode,omitempty" validate:"required_if=Version 0x3"`
 }
 
 type TransactionStatus struct {
@@ -297,18 +259,24 @@ type BroadcastedTransaction struct {
 func AdaptBroadcastedTransaction(broadcastedTxn *BroadcastedTransaction,
 	network *utils.Network,
 ) (core.Transaction, core.Class, *felt.Felt, error) {
-	// RPCv7 requests must set l2_gas to zero
-	if broadcastedTxn.ResourceBounds != nil {
-		(*broadcastedTxn.ResourceBounds)[ResourceL2Gas] = ResourceBounds{
-			MaxAmount:       new(felt.Felt).SetUint64(0),
-			MaxPricePerUnit: new(felt.Felt).SetUint64(0),
-		}
-	}
 	var feederTxn starknet.Transaction
 	if err := copier.Copy(&feederTxn, broadcastedTxn.Transaction); err != nil {
 		return nil, nil, nil, err
 	}
 
+	// RPCv7 requests must set l2_gas to zero
+	if broadcastedTxn.ResourceBounds != nil {
+		broadcastedTxn.ResourceBounds = &rpcv6.ResourceBoundsMap{
+			L1Gas: broadcastedTxn.ResourceBounds.L1Gas,
+			L2Gas: &rpcv6.ResourceBounds{
+				MaxAmount:       new(felt.Felt).SetUint64(0),
+				MaxPricePerUnit: new(felt.Felt).SetUint64(0),
+			},
+		}
+		// Copy doesn't covert the struct to enum correctly, so we need to adapt it
+		feederTxn.ResourceBounds = adaptToFeederResourceBounds(broadcastedTxn.ResourceBounds)
+	}
+
 	txn, err := sn2core.AdaptTransaction(&feederTxn)
 	if err != nil {
 		return nil, nil, nil, err
@@ -356,22 +324,37 @@ func AdaptBroadcastedTransaction(broadcastedTxn *BroadcastedTransaction,
 	return txn, declaredClass, paidFeeOnL1, nil
 }
 
-func adaptResourceBounds(rb map[core.Resource]core.ResourceBounds) map[Resource]ResourceBounds {
-	rpcResourceBounds := make(map[Resource]ResourceBounds)
-	for resource, bounds := range rb {
-		// ResourceL1DataGas is not supported in v7
-		if resource == core.ResourceL1DataGas {
-			continue
-		}
-
-		rpcResourceBounds[Resource(resource)] = ResourceBounds{
-			MaxAmount:       new(felt.Felt).SetUint64(bounds.MaxAmount),
-			MaxPricePerUnit: bounds.MaxPricePerUnit,
-		}
+func adaptResourceBounds(rb map[core.Resource]core.ResourceBounds) rpcv6.ResourceBoundsMap {
+	rpcResourceBounds := rpcv6.ResourceBoundsMap{
+		L1Gas: &rpcv6.ResourceBounds{
+			MaxAmount:       new(felt.Felt).SetUint64(rb[core.ResourceL1Gas].MaxAmount),
+			MaxPricePerUnit: rb[core.ResourceL1Gas].MaxPricePerUnit,
+		},
+		L2Gas: &rpcv6.ResourceBounds{
+			MaxAmount:       new(felt.Felt).SetUint64(rb[core.ResourceL2Gas].MaxAmount),
+			MaxPricePerUnit: rb[core.ResourceL2Gas].MaxPricePerUnit,
+		},
 	}
 	return rpcResourceBounds
 }
 
+func adaptToFeederResourceBounds(rb *rpcv6.ResourceBoundsMap) *map[starknet.Resource]starknet.ResourceBounds { //nolint:gocritic
+	if rb == nil {
+		return nil
+	}
+	feederResourceBounds := make(map[starknet.Resource]starknet.ResourceBounds)
+	feederResourceBounds[starknet.ResourceL1Gas] = starknet.ResourceBounds{
+		MaxAmount:       rb.L1Gas.MaxAmount,
+		MaxPricePerUnit: rb.L1Gas.MaxPricePerUnit,
+	}
+	feederResourceBounds[starknet.ResourceL2Gas] = starknet.ResourceBounds{
+		MaxAmount:       rb.L2Gas.MaxAmount,
+		MaxPricePerUnit: rb.L2Gas.MaxPricePerUnit,
+	}
+
+	return &feederResourceBounds
+}
+
 /****************************************************
 		Transaction Handlers
 *****************************************************/
```

### rpc/v7/transaction_test.go
```diff
@@ -191,16 +191,18 @@ func TestTransactionByBlockIdAndIndex(t *testing.T) {
 func adaptV6TxToV7(t *testing.T, tx *rpcv6.Transaction) *rpc.Transaction {
 	t.Helper()
 
-	var v7ResourceBounds *map[rpc.Resource]rpc.ResourceBounds
+	var v7ResourceBounds *rpcv6.ResourceBoundsMap
 	if tx.ResourceBounds != nil {
-		v7ResourceBoundsMap := make(map[rpc.Resource]rpc.ResourceBounds)
-		for r, rb := range *tx.ResourceBounds {
-			v7ResourceBoundsMap[rpc.Resource(r)] = rpc.ResourceBounds{
-				MaxAmount:       rb.MaxAmount,
-				MaxPricePerUnit: rb.MaxPricePerUnit,
-			}
+		v7ResourceBounds = &rpcv6.ResourceBoundsMap{
+			L1Gas: &rpcv6.ResourceBounds{
+				MaxAmount:       tx.ResourceBounds.L1Gas.MaxAmount,
+				MaxPricePerUnit: tx.ResourceBounds.L1Gas.MaxPricePerUnit,
+			},
+			L2Gas: &rpcv6.ResourceBounds{
+				MaxAmount:       tx.ResourceBounds.L2Gas.MaxAmount,
+				MaxPricePerUnit: tx.ResourceBounds.L2Gas.MaxPricePerUnit,
+			},
 		}
-		v7ResourceBounds = &v7ResourceBoundsMap
 	}
 
 	var v7NonceDAMode *rpc.DataAvailabilityMode
@@ -817,9 +819,9 @@ func TestAdaptTransaction(t *testing.T) {
 		expectedTx := &rpc.Transaction{
 			Type:    rpc.TxnInvoke,
 			Version: new(felt.Felt).SetUint64(3),
-			ResourceBounds: &map[rpc.Resource]rpc.ResourceBounds{
-				rpc.ResourceL1Gas: {MaxAmount: new(felt.Felt).SetUint64(1), MaxPricePerUnit: new(felt.Felt).SetUint64(2)},
-				rpc.ResourceL2Gas: {MaxAmount: new(felt.Felt).SetUint64(3), MaxPricePerUnit: new(felt.Felt).SetUint64(4)},
+			ResourceBounds: &rpcv6.ResourceBoundsMap{
+				L1Gas: &rpcv6.ResourceBounds{MaxAmount: new(felt.Felt).SetUint64(1), MaxPricePerUnit: new(felt.Felt).SetUint64(2)},
+				L2Gas: &rpcv6.ResourceBounds{MaxAmount: new(felt.Felt).SetUint64(3), MaxPricePerUnit: new(felt.Felt).SetUint64(4)},
 			},
 			Tip: new(felt.Felt).SetUint64(0),
 			// Those 4 fields are pointers to slice (the SliceHeader is allocated, it just refers to a nil array)
```

### rpc/v8/block_test.go
```diff
@@ -423,15 +423,19 @@ func TestBlockWithTxHashesV013(t *testing.T) {
 				Signature:          &tx.TransactionSignature,
 				CallData:           &tx.CallData,
 				EntryPointSelector: tx.EntryPointSelector,
-				ResourceBounds: &map[rpcv8.Resource]rpcv8.ResourceBounds{
-					rpcv8.ResourceL1Gas: {
+				ResourceBounds: &rpcv8.ResourceBoundsMap{
+					L1Gas: &rpcv8.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL1Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL1Gas].MaxPricePerUnit,
 					},
-					rpcv8.ResourceL2Gas: {
+					L2Gas: &rpcv8.ResourceBounds{
 						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL2Gas].MaxAmount),
 						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL2Gas].MaxPricePerUnit,
 					},
+					L1DataGas: &rpcv8.ResourceBounds{
+						MaxAmount:       new(felt.Felt).SetUint64(tx.ResourceBounds[core.ResourceL1DataGas].MaxAmount),
+						MaxPricePerUnit: tx.ResourceBounds[core.ResourceL1DataGas].MaxPricePerUnit,
+					},
 				},
 				Tip:                   new(felt.Felt).SetUint64(tx.Tip),
 				PaymasterData:         &tx.PaymasterData,
```

### rpc/v8/simulation.go
```diff
@@ -90,6 +90,25 @@ func (h *Handler) simulateTransactions(id BlockID, transactions []BroadcastedTra
 	return simulatedTransactions, httpHeader, nil
 }
 
+func isVersion3(version *felt.Felt) bool {
+	return version != nil && version.Equal(&rpcv6.RPCVersion3Value)
+}
+
+func checkTxHasSenderAddress(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnDeclare ||
+		tx.Transaction.Type == TxnInvoke) &&
+		isVersion3(tx.Transaction.Version) &&
+		tx.Transaction.SenderAddress == nil
+}
+
+func checkTxHasResourceBounds(tx *BroadcastedTransaction) bool {
+	return (tx.Transaction.Type == TxnInvoke ||
+		tx.Transaction.Type == TxnDeployAccount ||
+		tx.Transaction.Type == TxnDeclare) &&
+		isVersion3(tx.Transaction.Version) &&
+		tx.Transaction.ResourceBounds == nil
+}
+
 func prepareTransactions(transactions []BroadcastedTransaction, network *utils.Network) (
 	[]core.Transaction, []core.Class, []*felt.Felt, *jsonrpc.Error,
 ) {
@@ -98,7 +117,21 @@ func prepareTransactions(transactions []BroadcastedTransaction, network *utils.N
 	paidFeesOnL1 := make([]*felt.Felt, 0)
 
 	for idx := range transactions {
-		txn, declaredClass, paidFeeOnL1, aErr := adaptBroadcastedTransaction(&transactions[idx], network)
+		// Check for missing required fields in struct that can't be validated by
+		// jsonschema due to validation happening after omit empty
+		//
+		// TODO: as its expected that this will happen in other cases as well,
+		// it might be a good idea to implement a custom validator and unmarshal handler
+		// to solve this problem in a more elegant way
+		if checkTxHasSenderAddress(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "sender_address is required for this transaction type")
+		}
+
+		if checkTxHasResourceBounds(&transactions[idx]) {
+			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, "resource_bounds is required for this transaction type")
+		}
+
+		txn, declaredClass, paidFeeOnL1, aErr := AdaptBroadcastedTransaction(&transactions[idx], network)
 		if aErr != nil {
 			return nil, nil, nil, jsonrpc.Err(jsonrpc.InvalidParams, aErr.Error())
 		}
```
