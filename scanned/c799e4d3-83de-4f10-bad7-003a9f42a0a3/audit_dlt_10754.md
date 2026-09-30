# [?] fix data race in test

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-11-25
Source: https://github.com/multiversx/mx-chain-go/commit/b8de6ba43a62d539029bb85e352ae92aff698af1
Type: security-commit

## Details
fix data race in test

## Patch
### process/block/metablock_test.go
```diff
@@ -4354,7 +4354,7 @@ func TestMetaProcessor_prepareEpochStartBodyForTrigger(t *testing.T) {
 		hdrHash1 := []byte("hdrHash1")
 		hdrHash2 := []byte("hdrHash2")
 
-		metaBlockV3 = &block.MetaBlockV3{
+		metaBlock := &block.MetaBlockV3{
 			ExecutionResults: []*block.MetaExecutionResult{
 				{
 					ExecutionResult: &block.BaseMetaExecutionResult{
@@ -4401,7 +4401,7 @@ func TestMetaProcessor_prepareEpochStartBodyForTrigger(t *testing.T) {
 		args := createMockMetaArguments(coreComponents, dataComponents, bootstrapComponents, statusComponents)
 		mp, _ := blproc.NewMetaProcessor(args)
 
-		res, err := mp.PrepareEpochStartBodyForTrigger(metaBlockV3, nil)
+		res, err := mp.PrepareEpochStartBodyForTrigger(metaBlock, nil)
 		require.Nil(t, err)
 		require.Equal(t, &block.Body{MiniBlocks: mbs}, res)
 	})
```
