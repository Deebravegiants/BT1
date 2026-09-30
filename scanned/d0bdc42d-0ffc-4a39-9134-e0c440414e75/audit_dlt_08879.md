# [?] fix: Race condition in pipeline test (#3381)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2026-01-20
Source: https://github.com/NethermindEth/juno/commit/28f3402f906b52224be12bb0d370656843d28dec
Type: security-commit

## Details
fix: Race condition in pipeline test (#3381)

## Patch
### migration/pipeline/pipeline_test.go
```diff
@@ -60,22 +60,21 @@ func TestPipeline(t *testing.T) {
 
 	inputData := generateInputs()
 	go func() {
-		defer close(inputs)
 		for _, input := range inputData {
 			inputs <- input
 		}
+		close(inputs)
+		require.NoError(t, p.Wait())
 	}()
 
-	actualOutputs := make([]uint64, 0, itemCount)
-	go func() {
+	t.Run("Assert outputs", func(t *testing.T) {
+		expectedOutputs := generateOutputs(inputData)
+
+		actualOutputs := make([]uint64, 0, itemCount)
 		for output := range p.Outputs() {
 			actualOutputs = append(actualOutputs, output)
 		}
-	}()
 
-	require.NoError(t, p.Wait())
-	t.Run("Assert outputs", func(t *testing.T) {
-		expectedOutputs := generateOutputs(inputData)
 		require.ElementsMatch(t, expectedOutputs, actualOutputs)
 	})
 
```
