# [?] Fix non-determinism in integration test (#377)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2023-05-05
Source: https://github.com/babylonlabs-io/babylon/commit/a19d78ac4599a827b25c2c19e0e0deaf80ed4c14
Type: security-commit

## Details
Fix non-determinism in integration test (#377)

Fix non-determinism

## Patch
### test/integration_test.go
```diff
@@ -175,13 +175,13 @@ func TestBtcLightClientGenesis(t *testing.T) {
 
 func TestNodeProgress(t *testing.T) {
 	// Waiting for block 7, as tests are configured to run with epoch interval = 5,
-	// which means that at block 7 all clients will surely be in second epoch
+	// which means that at block 7 all clients will surely be in second epoch or later
 	waitForBlock(clients, 7)
 
 	for _, c := range clients {
 		currentEpoch := getCurrentEpoch(c)
-		if currentEpoch != 2 {
-			t.Errorf("Epoch after 7 blocks, should equal 2. Current epoch %d", currentEpoch)
+		if currentEpoch < 2 {
+			t.Errorf("Epoch after 7 blocks, should be at least larger or equal 2. Current epoch %d", currentEpoch)
 		}
 	}
 }
```
