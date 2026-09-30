# [?] fix data race in test

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-12-15
Source: https://github.com/multiversx/mx-chain-go/commit/a65195956abd630e4ec545be9620bc42678acb42
Type: security-commit

## Details
fix data race in test

## Patch
### epochStart/shardchain/triggerRegistry_test.go
```diff
@@ -141,8 +141,6 @@ func TestTrigger_LoadStateBackwardsCompatibility(t *testing.T) {
 	arguments.Epoch = epoch
 
 	t.Run("backwards compatibility", func(t *testing.T) {
-		t.Parallel()
-
 		bootStorer := genericMocks.NewStorerMock()
 		arguments.Storage = &storageStubs.ChainStorerStub{
 			GetStorerCalled: func(unitType dataRetriever.UnitType) (storage.Storer, error) {
@@ -165,8 +163,6 @@ func TestTrigger_LoadStateBackwardsCompatibility(t *testing.T) {
 	})
 
 	t.Run("header v1", func(t *testing.T) {
-		t.Parallel()
-
 		triggerRegistry := &block.ShardTriggerRegistry{
 			Epoch:                 epoch,
 			MetaEpoch:             epoch,
@@ -200,8 +196,6 @@ func TestTrigger_LoadStateBackwardsCompatibility(t *testing.T) {
 	})
 
 	t.Run("header v2", func(t *testing.T) {
-		t.Parallel()
-
 		triggerRegistry := &block.ShardTriggerRegistryV2{
 			Epoch:     epoch,
 			MetaEpoch: epoch,
@@ -240,8 +234,6 @@ func TestTrigger_LoadStateBackwardsCompatibility(t *testing.T) {
 	})
 
 	t.Run("header v3", func(t *testing.T) {
-		t.Parallel()
-
 		triggerRegistry := &block.ShardTriggerRegistryV3{
 			Epoch:                 epoch,
 			MetaEpoch:             epoch,
```

### process/sync/baseSync.go
```diff
@@ -1270,7 +1270,7 @@ func (boot *baseBootstrap) unmarshallTxByBlockType(
 			return nil, err
 		}
 	default:
-		return nil, fmt.Errorf("unsupported block type for dataPool: %d", blockType)
+		return nil, fmt.Errorf("unsupported block type: %d", blockType)
 	}
 
 	return tx, nil
```
