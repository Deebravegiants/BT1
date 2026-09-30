# [?] Fix exponentialBackoffer overflowing into negative, bump protocol version (#516)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2024-07-24
Source: https://github.com/filecoin-project/go-f3/commit/41e850b52221fad179aca1df2ff315d5715a6049
Type: security-commit

## Details
Fix exponentialBackoffer overflowing into negative, bump protocol version (#516)

* Fix exponentialBackoffer overflowing into negative

Signed-off-by: Jakub Sztandera <oss@kubuxu.com>

* Bump protocol version

Signed-off-by: Jakub Sztandera <oss@kubuxu.com>

* Bump default protocol version

Signed-off-by: Jakub Sztandera <oss@kubuxu.com>

* Bump version

Signed-off-by: Jakub Sztandera <oss@kubuxu.com>

---------

Signed-off-by: Jakub Sztandera <oss@kubuxu.com>

## Patch
### gpbft/options.go
```diff
@@ -113,12 +113,12 @@ func WithRebroadcastBackoff(exponent float64, base, max time.Duration) Option {
 	}
 }
 
-func exponentialBackoffer(exponent float64, base, max time.Duration) func(attempt int) time.Duration {
+func exponentialBackoffer(exponent float64, base, maxBackoff time.Duration) func(attempt int) time.Duration {
 	return func(attempt int) time.Duration {
-		nextBackoff := time.Duration(float64(base) * math.Pow(exponent, float64(attempt)))
-		if nextBackoff > max {
-			return max
+		nextBackoff := float64(base) * math.Pow(exponent, float64(attempt))
+		if nextBackoff > float64(maxBackoff) {
+			return maxBackoff
 		}
-		return nextBackoff
+		return maxBackoff
 	}
 }
```

### gpbft/options_test.go
```diff
@@ -0,0 +1,18 @@
+package gpbft
+
+import (
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+)
+
+func Test_exponentialBackoffer(t *testing.T) {
+	maxBackoff := 30 * time.Second
+	backoffer := exponentialBackoffer(1.3, 3*time.Second, maxBackoff)
+	for i := 0; i < 10_000; i++ {
+		backoff := backoffer(i)
+		require.Positivef(t, backoff, "at %d", i)
+		require.LessOrEqualf(t, backoff, maxBackoff, "at %d", i)
+	}
+}
```

### manifest/manifest.go
```diff
@@ -14,7 +14,7 @@ import (
 	"github.com/ipfs/go-datastore"
 )
 
-const VersionCapability = 1
+const VersionCapability = 2
 
 var (
 	DefaultCommitteeLookback uint64 = 10
@@ -245,7 +245,7 @@ func LocalDevnetManifest() *Manifest {
 	rng := make([]byte, 4)
 	_, _ = rand.Read(rng)
 	m := &Manifest{
-		ProtocolVersion:     1,
+		ProtocolVersion:     VersionCapability,
 		NetworkName:         gpbft.NetworkName(fmt.Sprintf("localnet-%X", rng)),
 		BootstrapEpoch:      1000,
 		CommitteeLookback:   DefaultCommitteeLookback,
```

### version.json
```diff
@@ -1,3 +1,3 @@
 {
-  "version": "v0.0.5"
+  "version": "v0.0.6"
 }
```
