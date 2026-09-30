# [?] remove buffered channel from simulated api, deadlock issue was fixed in https://github.com/ethereum/go-ethereum/pull/30264

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-02-27
Source: https://github.com/OffchainLabs/go-ethereum/commit/1c87517682bf0596b79a07b16f7dd1ebeb9e6568
Type: security-commit

## Details
remove buffered channel from simulated api, deadlock issue was fixed in https://github.com/ethereum/go-ethereum/pull/30264

## Patch
### eth/catalyst/simulated_beacon_api.go
```diff
@@ -46,10 +46,7 @@ func newSimulatedBeaconAPI(sim *SimulatedBeacon) *simulatedBeaconAPI {
 // transaction is received.
 func (a *simulatedBeaconAPI) loop() {
 	var (
-		// Arbitrum: we need to make newTxs a buffered channel because by the current design of simulated beacon
-		// it would deadlock with this cycle a.sim.Commit() -> txpool.Sync() -> subpools reset -> update feeds (newTxs is one of the receivers)
-		// Note: capacity of this channel should be the worst-case estimate of number of transactions all arriving simultaneously to the pool
-		newTxs    = make(chan core.NewTxsEvent, 15)
+		newTxs    = make(chan core.NewTxsEvent)
 		newWxs    = make(chan newWithdrawalsEvent)
 		newTxsSub = a.sim.eth.TxPool().SubscribeTransactions(newTxs, true)
 		newWxsSub = a.sim.withdrawals.subscribe(newWxs)
```

### eth/catalyst/simulated_beacon_test.go
```diff
@@ -141,67 +141,6 @@ func TestSimulatedBeaconSendWithdrawals(t *testing.T) {
 	}
 }
 
-func TestSimulatedBeaconAPIDeadlocksInExtremeConditions(t *testing.T) {
-	txs := make(map[common.Hash]*types.Transaction)
-
-	var (
-		// testKey is a private key to use for funding a tester account.
-		testKey, _ = crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
-
-		// testAddr is the Ethereum address of the tester account.
-		testAddr = crypto.PubkeyToAddress(testKey.PublicKey)
-	)
-
-	// short period (1 second) for testing purposes
-	var gasLimit uint64 = 10_000_000
-	genesis := core.DeveloperGenesisBlock(gasLimit, &testAddr)
-	node, ethService, mock := startSimulatedBeaconEthService(t, genesis, 1)
-	_ = mock
-	defer node.Close()
-
-	// simulated beacon api
-	mockApi := &simulatedBeaconAPI{mock}
-	go mockApi.loop()
-
-	chainHeadCh := make(chan core.ChainHeadEvent, 10)
-	subscription := ethService.BlockChain().SubscribeChainHeadEvent(chainHeadCh)
-	defer subscription.Unsubscribe()
-
-	// generate a bunch of transactions to overload simulated beacon api
-	// current capacity of core.NewTxsEvent channel is 15, we send 30 txs
-	signer := types.NewEIP155Signer(ethService.BlockChain().Config().ChainID)
-	for i := 0; i < 30; i++ {
-		tx, err := types.SignTx(types.NewTransaction(uint64(i), common.Address{}, big.NewInt(1000), params.TxGas, big.NewInt(params.InitialBaseFee), nil), signer, testKey)
-		if err != nil {
-			t.Fatalf("error signing transaction, err=%v", err)
-		}
-		txs[tx.Hash()] = tx
-
-		if err := ethService.APIBackend.SendTx(context.Background(), tx); err != nil {
-			t.Fatal("SendTx failed", err)
-		}
-	}
-
-	includedTxs := make(map[common.Hash]struct{})
-
-	timer := time.NewTimer(12 * time.Second)
-	for {
-		select {
-		case evt := <-chainHeadCh:
-			for _, includedTx := range evt.Block.Transactions() {
-				includedTxs[includedTx.Hash()] = struct{}{}
-			}
-
-			// ensure all withdrawals/txs included. this will take two blocks b/c number of withdrawals > 10
-			if len(includedTxs) == len(txs) {
-				t.Fatal("all txs were included, the simulated beacon api did not deadlock")
-			}
-		case <-timer.C:
-			return
-		}
-	}
-}
-
 // Tests that zero-period dev mode can handle a lot of simultaneous
 // transactions/withdrawals
 func TestOnDemandSpam(t *testing.T) {
```
