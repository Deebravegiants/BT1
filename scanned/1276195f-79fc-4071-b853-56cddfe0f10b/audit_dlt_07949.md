# [?] Fix `TestVMUpgradeBytesPrecompile` race condition flake  (#1699)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-08-25
Source: https://github.com/ava-labs/avalanchego/commit/83d2fe5ad9784149d22d28c23bacd86d8d0544a7
Type: security-commit

## Details
Fix `TestVMUpgradeBytesPrecompile` race condition flake  (#1699)

Co-authored-by: Austin Larson <austin.larson@avalabs.org>

## Patch
### plugin/evm/vm_upgrade_bytes_test.go
```diff
@@ -57,6 +57,11 @@ func TestVMUpgradeBytesPrecompile(t *testing.T) {
 		genesisJSON: genesisJSONSubnetEVM,
 		upgradeJSON: string(upgradeBytesJSON),
 	})
+	defer func() {
+		if err := tvm.vm.Shutdown(context.Background()); err != nil {
+			t.Fatal(err)
+		}
+	}()
 
 	tvm.vm.clock.Set(enableAllowListTimestamp)
 
@@ -81,11 +86,6 @@ func TestVMUpgradeBytesPrecompile(t *testing.T) {
 		t.Fatalf("expected ErrSenderAddressNotAllowListed, got: %s", err)
 	}
 
-	// shutdown the vm
-	if err := tvm.vm.Shutdown(context.Background()); err != nil {
-		t.Fatal(err)
-	}
-
 	// prepare the new upgrade bytes to disable the TxAllowList
 	disableAllowListTimestamp := tvm.vm.clock.Time().Add(10 * time.Hour) // arbitrary choice
 	upgradeConfig.PrecompileUpgrades = append(
@@ -99,46 +99,46 @@ func TestVMUpgradeBytesPrecompile(t *testing.T) {
 		t.Fatalf("could not marshal upgradeConfig to json: %s", err)
 	}
 
-	// restart the vm
-
 	// Reset metrics to allow re-initialization
 	tvm.vm.ctx.Metrics = metrics.NewPrefixGatherer()
 
-	if err := tvm.vm.Initialize(
+	// restart the vm with the same stateful params
+	newVM := &VM{}
+	if err := newVM.Initialize(
 		context.Background(), tvm.vm.ctx, tvm.db, []byte(genesisJSONSubnetEVM), upgradeBytesJSON, []byte{}, []*commonEng.Fx{}, tvm.appSender,
 	); err != nil {
 		t.Fatal(err)
 	}
 	defer func() {
-		if err := tvm.vm.Shutdown(context.Background()); err != nil {
+		if err := newVM.Shutdown(context.Background()); err != nil {
 			t.Fatal(err)
 		}
 	}()
 	// Set the VM's state to NormalOp to initialize the tx pool.
-	if err := tvm.vm.SetState(context.Background(), snow.Bootstrapping); err != nil {
+	if err := newVM.SetState(context.Background(), snow.Bootstrapping); err != nil {
 		t.Fatal(err)
 	}
-	if err := tvm.vm.SetState(context.Background(), snow.NormalOp); err != nil {
+	if err := newVM.SetState(context.Background(), snow.NormalOp); err != nil {
 		t.Fatal(err)
 	}
 	newTxPoolHeadChan := make(chan core.NewTxPoolReorgEvent, 1)
-	tvm.vm.txPool.SubscribeNewReorgEvent(newTxPoolHeadChan)
-	tvm.vm.clock.Set(disableAllowListTimestamp)
+	newVM.txPool.SubscribeNewReorgEvent(newTxPoolHeadChan)
+	newVM.clock.Set(disableAllowListTimestamp)
 
 	// Make a block, previous rules still apply (TxAllowList is active)
 	// Submit a successful transaction
-	errs = tvm.vm.txPool.AddRemotesSync([]*types.Transaction{signedTx0})
+	errs = newVM.txPool.AddRemotesSync([]*types.Transaction{signedTx0})
 	if err := errs[0]; err != nil {
 		t.Fatalf("Failed to add tx at index: %s", err)
 	}
 
 	// Submit a rejected transaction, should throw an error
-	errs = tvm.vm.txPool.AddRemotesSync([]*types.Transaction{signedTx1})
+	errs = newVM.txPool.AddRemotesSync([]*types.Transaction{signedTx1})
 	if err := errs[0]; !errors.Is(err, vmerrors.ErrSenderAddressNotAllowListed) {
 		t.Fatalf("expected ErrSenderAddressNotAllowListed, got: %s", err)
 	}
 
-	blk := issueAndAccept(t, tvm.vm)
+	blk := issueAndAccept(t, newVM)
 
 	// Verify that the constructed block only has the whitelisted tx
 	block := blk.(*chain.BlockWrapper).Block.(*Block).ethBlock
@@ -154,13 +154,13 @@ func TestVMUpgradeBytesPrecompile(t *testing.T) {
 	<-newTxPoolHeadChan // wait for new head in tx pool
 
 	// retry the rejected Tx, which should now succeed
-	errs = tvm.vm.txPool.AddRemotesSync([]*types.Transaction{signedTx1})
+	errs = newVM.txPool.AddRemotesSync([]*types.Transaction{signedTx1})
 	if err := errs[0]; err != nil {
 		t.Fatalf("Failed to add tx at index: %s", err)
 	}
 
-	tvm.vm.clock.Set(tvm.vm.clock.Time().Add(2 * time.Second)) // add 2 seconds for gas fee to adjust
-	blk = issueAndAccept(t, tvm.vm)
+	newVM.clock.Set(newVM.clock.Time().Add(2 * time.Second)) // add 2 seconds for gas fee to adjust
+	blk = issueAndAccept(t, newVM)
 
 	// Verify that the constructed block only has the previously rejected tx
 	block = blk.(*chain.BlockWrapper).Block.(*Block).ethBlock
```
