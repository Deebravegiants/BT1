# [?] Fixes coinbase balance check unsigned integer underflow in mev-boost payload validation api (#162)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/builder
Published: 2024-06-26
Source: https://github.com/flashbots/builder/commit/df9c765067d57ab4b2d0ad39dbb156cbe4965778
Type: security-commit

## Details
Fixes coinbase balance check unsigned integer underflow in mev-boost payload validation api (#162)

* Adjusts how coinbase diff-based payment validation is performed to avoid any possibly underflowing substractions

## Patch
### core/blockchain.go
```diff
@@ -2494,13 +2494,14 @@ func (bc *BlockChain) ValidatePayload(block *types.Block, feeRecipient common.Ad
 		return err
 	}
 
-	feeRecipientBalanceDelta := new(uint256.Int).Set(statedb.GetBalance(feeRecipient))
-	feeRecipientBalanceDelta.Sub(feeRecipientBalanceDelta, feeRecipientBalanceBefore)
+	feeRecipientBalanceAfter := new(uint256.Int).Set(statedb.GetBalance(feeRecipient))
+
+	amtBeforeOrWithdrawn := new(uint256.Int).Set(feeRecipientBalanceBefore)
 	if excludeWithdrawals {
 		for _, w := range block.Withdrawals() {
 			if w.Address == feeRecipient {
 				amount := new(uint256.Int).Mul(new(uint256.Int).SetUint64(w.Amount), uint256.NewInt(params.GWei))
-				feeRecipientBalanceDelta.Sub(feeRecipientBalanceDelta, amount)
+				amtBeforeOrWithdrawn = amtBeforeOrWithdrawn.Add(amtBeforeOrWithdrawn, amount)
 			}
 		}
 	}
@@ -2529,7 +2530,10 @@ func (bc *BlockChain) ValidatePayload(block *types.Block, feeRecipient common.Ad
 
 	// Validate proposer payment
 
-	if useBalanceDiffProfit {
+	if useBalanceDiffProfit && feeRecipientBalanceAfter.Cmp(amtBeforeOrWithdrawn) >= 0 {
+		feeRecipientBalanceDelta := new(uint256.Int).Set(feeRecipientBalanceAfter)
+		feeRecipientBalanceDelta = feeRecipientBalanceDelta.Sub(feeRecipientBalanceDelta, amtBeforeOrWithdrawn)
+
 		uint256ExpectedProfit, ok := uint256.FromBig(expectedProfit)
 		if !ok {
 			if feeRecipientBalanceDelta.Cmp(uint256ExpectedProfit) >= 0 {
```

### eth/block-validation/api_test.go
```diff
@@ -845,6 +845,99 @@ func executableDataToBlockValidationRequest(execData *engine.ExecutableData, pro
 	return blockRequest, nil
 }
 
+func TestValidateBuilderSubmissionV2_CoinbasePaymentUnderflow(t *testing.T) {
+	genesis, preMergeBlocks := generatePreMergeChain(20)
+	lastBlock := preMergeBlocks[len(preMergeBlocks)-1]
+	time := lastBlock.Time() + 5
+	genesis.Config.ShanghaiTime = &time
+	n, ethservice := startEthService(t, genesis, preMergeBlocks)
+	ethservice.Merger().ReachTTD()
+	defer n.Close()
+
+	api := NewBlockValidationAPI(ethservice, nil, true, true)
+
+	baseFee := eip1559.CalcBaseFee(ethservice.BlockChain().Config(), lastBlock.Header())
+	txs := make(types.Transactions, 0)
+
+	statedb, _ := ethservice.BlockChain().StateAt(lastBlock.Root())
+	nonce := statedb.GetNonce(testAddr)
+	validatorNonce := statedb.GetNonce(testValidatorAddr)
+	signer := types.LatestSigner(ethservice.BlockChain().Config())
+
+	expectedProfit := uint64(0)
+
+	tx1, _ := types.SignTx(types.NewTransaction(nonce, common.Address{0x16}, big.NewInt(10), 21000, big.NewInt(2*baseFee.Int64()), nil), signer, testKey)
+	txs = append(txs, tx1)
+	expectedProfit += 21000 * baseFee.Uint64()
+
+	// this tx will use 56996 gas
+	tx2, _ := types.SignTx(types.NewContractCreation(nonce+1, new(big.Int), 1000000, big.NewInt(2*baseFee.Int64()), logCode), signer, testKey)
+	txs = append(txs, tx2)
+	expectedProfit += 56996 * baseFee.Uint64()
+
+	tx3, _ := types.SignTx(types.NewTransaction(nonce+2, testAddr, big.NewInt(10), 21000, baseFee, nil), signer, testKey)
+	txs = append(txs, tx3)
+
+	// Test transferring out more than the profit
+	toTransferOut := 2*expectedProfit - 21000*baseFee.Uint64()
+	tx4, _ := types.SignTx(types.NewTransaction(validatorNonce, testAddr, big.NewInt(int64(toTransferOut)), 21000, baseFee, nil), signer, testValidatorKey)
+	txs = append(txs, tx4)
+	expectedProfit += 7
+
+	withdrawals := []*types.Withdrawal{
+		{
+			Index:     0,
+			Validator: 1,
+			Amount:    100,
+			Address:   testAddr,
+		},
+		{
+			Index:     1,
+			Validator: 1,
+			Amount:    100,
+			Address:   testAddr,
+		},
+	}
+	withdrawalsRoot := types.DeriveSha(types.Withdrawals(withdrawals), trie.NewStackTrie(nil))
+
+	buildBlockArgs := buildBlockArgs{
+		parentHash:    lastBlock.Hash(),
+		parentRoot:    lastBlock.Root(),
+		feeRecipient:  testValidatorAddr,
+		txs:           txs,
+		random:        common.Hash{},
+		number:        lastBlock.NumberU64() + 1,
+		gasLimit:      lastBlock.GasLimit(),
+		timestamp:     lastBlock.Time() + 5,
+		extraData:     nil,
+		baseFeePerGas: baseFee,
+		withdrawals:   withdrawals,
+	}
+
+	execData, err := buildBlock(buildBlockArgs, ethservice.BlockChain())
+	require.NoError(t, err)
+
+	value := big.NewInt(int64(expectedProfit))
+
+	req, err := executableDataToBlockValidationRequest(execData, testValidatorAddr, value, withdrawalsRoot)
+	require.NoError(t, err)
+	require.ErrorContains(t, api.ValidateBuilderSubmissionV2(req), "payment tx not to the proposers fee recipient")
+
+	// try to claim less profit than expected, should work
+	value.SetUint64(expectedProfit - 1)
+
+	req, err = executableDataToBlockValidationRequest(execData, testValidatorAddr, value, withdrawalsRoot)
+	require.NoError(t, err)
+	require.ErrorContains(t, api.ValidateBuilderSubmissionV2(req), "payment tx not to the proposers fee recipient")
+
+	// try to claim more profit than expected, should fail
+	value.SetUint64(expectedProfit + 1)
+
+	req, err = executableDataToBlockValidationRequest(execData, testValidatorAddr, value, withdrawalsRoot)
+	require.NoError(t, err)
+	require.ErrorContains(t, api.ValidateBuilderSubmissionV2(req), "payment")
+}
+
 // This tests payment when the proposer fee recipient is the same as the coinbase
 func TestValidateBuilderSubmissionV2_CoinbasePaymentDefault(t *testing.T) {
 	genesis, preMergeBlocks := generatePreMergeChain(20)
```
