# [?] fix Jitter panic (#9370)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-05-31
Source: https://github.com/smartcontractkit/ccip/commit/5e728573b3318314adcfa4dc8c35d98d5de8a8d2
Type: security-commit

## Details
fix Jitter panic (#9370)

## Patch
### core/utils/utils.go
```diff
@@ -10,6 +10,7 @@ import (
 	"errors"
 	"fmt"
 	"io"
+	"math"
 	"math/big"
 	mrand "math/rand"
 	"sort"
@@ -1019,7 +1020,10 @@ func WithJitter(d time.Duration) time.Duration {
 	if d == 0 {
 		return 0
 	}
-	jitter := mrand.Intn(int(d) / 5)
+	// ensure non-zero arg to Intn to avoid panic
+	max := math.Max(float64(d.Abs())/5.0, 1.)
+	// #nosec - non critical randomness
+	jitter := mrand.Intn(int(max))
 	jitter = jitter - (jitter / 2)
 	return time.Duration(int(d) + jitter)
 }
```
