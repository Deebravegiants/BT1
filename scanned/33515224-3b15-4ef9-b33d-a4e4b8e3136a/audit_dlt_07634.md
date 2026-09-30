# [?] les/utils: protect against WeightedRandomSelect overflow (#21839)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-11-23
Source: https://github.com/ethereum/go-ethereum/commit/bddf5aaa2f737569e5f96de3676c5123b82e60f0
Type: security-commit

## Details
les/utils: protect against WeightedRandomSelect overflow (#21839)

Also fixes a bug in les/flowcontrol that caused the overflow.

## Patch
### les/flowcontrol/control.go
```diff
@@ -19,6 +19,7 @@ package flowcontrol
 
 import (
 	"fmt"
+	"math"
 	"sync"
 	"time"
 
@@ -316,6 +317,9 @@ func (node *ServerNode) CanSend(maxCost uint64) (time.Duration, float64) {
 	node.lock.RLock()
 	defer node.lock.RUnlock()
 
+	if node.params.BufLimit == 0 {
+		return time.Duration(math.MaxInt64), 0
+	}
 	now := node.clock.Now()
 	node.recalcBLE(now)
 	maxCost += uint64(safetyMargin) * node.params.MinRecharge / uint64(fcTimeConst)
```

### les/utils/weighted_select.go
```diff
@@ -17,7 +17,10 @@
 package utils
 
 import (
+	"math"
 	"math/rand"
+
+	"github.com/ethereum/go-ethereum/log"
 )
 
 type (
@@ -54,6 +57,14 @@ func (w *WeightedRandomSelect) IsEmpty() bool {
 
 // setWeight sets an item's weight to a specific value (removes it if zero)
 func (w *WeightedRandomSelect) setWeight(item WrsItem, weight uint64) {
+	if weight > math.MaxInt64-w.root.sumWeight {
+		// old weight is still included in sumWeight, remove and check again
+		w.setWeight(item, 0)
+		if weight > math.MaxInt64-w.root.sumWeight {
+			log.Error("WeightedRandomSelect overflow", "sumWeight", w.root.sumWeight, "new weight", weight)
+			weight = math.MaxInt64 - w.root.sumWeight
+		}
+	}
 	idx, ok := w.idx[item]
 	if ok {
 		w.root.setWeight(idx, weight)
```
