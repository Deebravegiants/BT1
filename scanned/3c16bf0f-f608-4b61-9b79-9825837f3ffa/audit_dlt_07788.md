# [?] fixed erroneous panic (#12450)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-05-23
Source: https://github.com/OffchainLabs/prysm/commit/cd0f814f2e4414878e783df996605c458ecf0f5e
Type: security-commit

## Details
fixed erroneous panic (#12450)

## Patch
### beacon-chain/forkchoice/doubly-linked-tree/reorg_late_blocks.go
```diff
@@ -85,7 +85,7 @@ func (f *ForkChoice) ShouldOverrideFCU() (override bool) {
 
 	// Only orphan a block if the parent LMD vote is strong
 	if parent.weight*100 < f.store.committeeWeight*params.BeaconConfig().ReorgParentWeightThreshold {
-		panic(f.store.committeeWeight)
+		return
 	}
 	return true
 }
```

### beacon-chain/forkchoice/doubly-linked-tree/reorg_late_blocks_test.go
```diff
@@ -84,6 +84,12 @@ func TestForkChoice_ShouldOverrideFCU(t *testing.T) {
 		require.Equal(t, false, f.ShouldOverrideFCU())
 		f.store.headNode.parent = saved
 	})
+	t.Run("parent is weak", func(t *testing.T) {
+		saved := f.store.headNode.parent.weight
+		f.store.headNode.parent.weight = 0
+		require.Equal(t, false, f.ShouldOverrideFCU())
+		f.store.headNode.parent.weight = saved
+	})
 	t.Run("Head is strong", func(t *testing.T) {
 		f.store.headNode.weight = f.store.committeeWeight
 		require.Equal(t, false, f.ShouldOverrideFCU())
@@ -169,6 +175,12 @@ func TestForkChoice_GetProposerHead(t *testing.T) {
 		require.Equal(t, childRoot, f.GetProposerHead())
 		f.store.headNode.parent = saved
 	})
+	t.Run("parent is weak", func(t *testing.T) {
+		saved := f.store.headNode.parent.weight
+		f.store.headNode.parent.weight = 0
+		require.Equal(t, false, f.ShouldOverrideFCU())
+		f.store.headNode.parent.weight = saved
+	})
 	t.Run("Head is strong", func(t *testing.T) {
 		f.store.headNode.weight = f.store.committeeWeight
 		require.Equal(t, childRoot, f.GetProposerHead())
```
