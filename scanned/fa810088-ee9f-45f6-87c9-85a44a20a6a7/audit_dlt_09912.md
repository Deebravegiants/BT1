# [?] Merge pull request #937 from hyunsooda/fix/nondeterministic-bundle-ordering

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-16
Source: https://github.com/kaiachain/kaia/commit/1cd31ff502cbf1e2e7826ec03400a26f875eccd1
Type: security-commit

## Details
Merge pull request #937 from hyunsooda/fix/nondeterministic-bundle-ordering

work/builder: fix non-deterministic auction bundle ordering

## Patch
### work/builder/builder.go
```diff
@@ -341,12 +341,19 @@ func coordinateTargetTxHash(bundles []*Bundle) []*Bundle {
 
 	newBundles := make([]*Bundle, 0, len(bundles))
 	sameTargetTxHashBundles := make(map[common.Hash][]*Bundle)
+	// Emit groups in first-seen (input) order. Ranging over the map directly
+	// uses Go's randomized iteration order, which is nondeterministic.
+	order := make([]common.Hash, 0, len(bundles))
 
 	for _, bundle := range bundles {
+		if _, ok := sameTargetTxHashBundles[bundle.TargetTxHash]; !ok {
+			order = append(order, bundle.TargetTxHash)
+		}
 		sameTargetTxHashBundles[bundle.TargetTxHash] = append(sameTargetTxHashBundles[bundle.TargetTxHash], bundle)
 	}
 
-	for _, list := range sameTargetTxHashBundles {
+	for _, key := range order {
+		list := sameTargetTxHashBundles[key]
 		if len(list) == 1 {
 			newBundles = append(newBundles, list[0])
 			continue
```

### work/builder/builder_test.go
```diff
@@ -581,3 +581,47 @@ func TestCoordinateTargetTxHash(t *testing.T) {
 		})
 	}
 }
+
+// Regression test: an auction bundle targeting a gasless bundle's last tx must
+// stay adjacent to its target after coordinateTargetTxHash, regardless of the
+// (previously map-randomized) group order.
+func TestCoordinateTargetTxHashDeterministicWithGaslessTarget(t *testing.T) {
+	approveTx := types.NewTransaction(0, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil)
+	swapTx := types.NewTransaction(1, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil)
+	targetTx := types.NewTransaction(2, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil)
+	fillerTx := types.NewTransaction(3, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil)
+	txs := []*types.Transaction{approveTx, swapTx, targetTx, fillerTx}
+
+	gen := func(nonce uint64) (*types.Transaction, error) {
+		return types.NewTransaction(nonce, common.Address{}, big.NewInt(0), 0, big.NewInt(0), nil), nil
+	}
+	lendGen := NewTxOrGenFromGen(gen, common.Hash{0xaa})
+	bidGen := NewTxOrGenFromGen(gen, common.Hash{0xbb})
+
+	// Gasless bundle owns swap as its last tx; auction bundle targets swap.
+	// Module registration order places gasless before auction in the input.
+	newInput := func() []*Bundle {
+		gasless := NewBundle([]*TxOrGen{lendGen, NewTxOrGenFromTx(approveTx), NewTxOrGenFromTx(swapTx)}, targetTx.Hash(), false)
+		auction := NewBundle([]*TxOrGen{bidGen}, swapTx.Hash(), true)
+		return []*Bundle{gasless, auction}
+	}
+
+	in := newInput()
+	require.False(t, in[0].IsConflict(in[1]), "auction targeting the gasless bundle's last tx must be allowed")
+
+	for i := 0; i < 100; i++ {
+		incorporated, err := IncorporateBundleTx(txs, coordinateTargetTxHash(newInput()))
+		require.NoError(t, err)
+
+		bidIdx := -1
+		for j, txOrGen := range incorporated {
+			if txOrGen.Id == bidGen.Id {
+				bidIdx = j
+				break
+			}
+		}
+		require.NotEqual(t, -1, bidIdx, "auction bid must be present")
+		require.Greater(t, bidIdx, 0, "auction bid must not be first; its target must precede it")
+		require.Equal(t, swapTx.Hash(), incorporated[bidIdx-1].Id, "auction bid must immediately follow its target swap tx")
+	}
+}
```
