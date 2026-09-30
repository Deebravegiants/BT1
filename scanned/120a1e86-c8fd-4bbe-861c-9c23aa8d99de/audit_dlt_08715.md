# [?] fix race condition

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-04-02
Source: https://github.com/OffchainLabs/nitro/commit/65220729d0dc8d6e76f48d8be0dc382a1ed6c887
Type: security-commit

## Details
fix race condition

## Patch
### das/aggregator_test.go
```diff
@@ -248,9 +248,9 @@ func testConfigurableStorageFailures(t *testing.T, shouldFailAggregation bool) {
 }
 
 func initTest(t *testing.T) int {
+	flag.Parse()
 	t.Parallel()
 	seed := time.Now().UnixNano()
-	flag.Parse()
 	if len(*seedFlag) > 0 {
 		var err error
 		intSeed, err := strconv.Atoi(*seedFlag)
```
