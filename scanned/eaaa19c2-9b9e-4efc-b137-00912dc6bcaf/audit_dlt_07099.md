# [?] Fix data race in monitoring test (#11032)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2022-07-14
Source: https://github.com/OffchainLabs/prysm/commit/2162ffb05fdf471e8504a914e8e34a9434f73fad
Type: security-commit

## Details
Fix data race in monitoring test (#11032)

Signed-off-by: Luca Georges Francois <luca.georges-francois@epitech.eu>

Co-authored-by: terencechain <terence@prysmaticlabs.com>
Co-authored-by: Raul Jordan <raul@prysmaticlabs.com>

## Patch
### beacon-chain/monitor/service_test.go
```diff
@@ -172,7 +172,9 @@ func TestStart(t *testing.T) {
 	time.Sleep(1000 * time.Millisecond)
 	require.LogsContain(t, hook, "Synced to head epoch, starting reporting performance")
 	require.LogsContain(t, hook, "\"Starting service\" ValidatorIndices=\"[1 2 12 15]\"")
+	s.Lock()
 	require.Equal(t, s.isLogging, true, "monitor is not running")
+	s.Unlock()
 }
 
 func TestInitializePerformanceStructures(t *testing.T) {
```
