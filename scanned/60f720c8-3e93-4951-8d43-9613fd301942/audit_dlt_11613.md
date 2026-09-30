# [?] pricing: fix panic when min=max

## Summary
Severity: Unknown
Chain: Akash
Component: akash-network/node
Published: 2018-07-31
Source: https://github.com/akash-network/node/commit/b150118b53ff846080b9f61e88bb98fc290cc4e8
Type: security-commit

## Details
pricing: fix panic when min=max

## Patch
### provider/bidengine/order.go
```diff
@@ -3,14 +3,12 @@ package bidengine
 import (
 	"bytes"
 	"context"
-	"math/rand"
 
 	lifecycle "github.com/boz/go-lifecycle"
 	"github.com/ovrclk/akash/provider/cluster"
 	"github.com/ovrclk/akash/provider/event"
 	"github.com/ovrclk/akash/provider/session"
 	"github.com/ovrclk/akash/types"
-	"github.com/ovrclk/akash/types/unit"
 	"github.com/ovrclk/akash/util/runner"
 	"github.com/ovrclk/akash/validation"
 	"github.com/tendermint/tmlibs/log"
@@ -177,7 +175,7 @@ loop:
 
 			reservation = result.Value().(cluster.Reservation)
 
-			price := o.calculatePrice(reservation.Resources())
+			price := calculatePrice(reservation.Resources())
 
 			o.log.Debug("submitting fulfillment", "price", price)
 
@@ -246,33 +244,4 @@ func (o *order) shouldBid(group *types.DeploymentGroup) bool {
 		return false
 	}
 	return true
-
-}
-
-func (o *order) calculatePrice(resources types.ResourceList) uint64 {
-
-	// TODO: catch overflow
-	var (
-		mem  int64
-		rmax int64
-	)
-
-	cfg := validation.Config()
-
-	for _, group := range resources.GetResources() {
-		rmax += int64(group.Price * uint64(group.Count))
-		mem += int64(group.Unit.Memory * uint64(group.Count))
-	}
-
-	cmin := uint64(float64(mem) * float64(cfg.MinGroupMemPrice) / float64(unit.Gi))
-	cmax := uint64(float64(mem) * float64(cfg.MaxGroupMemPrice) / float64(unit.Gi))
-
-	if cmax > uint64(rmax) {
-		cmax = uint64(rmax)
-	}
-	if cmax == 0 {
-		cmax = 1
-	}
-
-	return uint64(rand.Int63n(int64(cmax-cmin)) + int64(cmin))
 }
```

### provider/bidengine/pricing.go
```diff
@@ -0,0 +1,48 @@
+package bidengine
+
+import (
+	"math/rand"
+
+	"github.com/ovrclk/akash/types"
+	"github.com/ovrclk/akash/types/unit"
+	"github.com/ovrclk/akash/validation"
+)
+
+func calculatePrice(resources types.ResourceList) uint64 {
+	min, max := calculatePriceRange(resources)
+
+	if max == min {
+		return max
+	}
+
+	return uint64(rand.Int63n(int64(max-min)) + int64(min))
+}
+
+func calculatePriceRange(resources types.ResourceList) (uint64, uint64) {
+
+	// TODO: catch overflow
+	var (
+		mem  uint64
+		rmax uint64
+	)
+
+	cfg := validation.Config()
+
+	for _, group := range resources.GetResources() {
+		rmax += group.Price * uint64(group.Count)
+		mem += group.Unit.Memory * uint64(group.Count)
+	}
+
+	cmin := uint64(float64(mem) * float64(cfg.MinGroupMemPrice) / float64(unit.Gi))
+	cmax := uint64(float64(mem) * float64(cfg.MaxGroupMemPrice) / float64(unit.Gi))
+
+	if cmax > rmax {
+		cmax = rmax
+	}
+	if cmax == 0 {
+		cmax = 1
+	}
+
+	return cmin, cmax
+
+}
```

### provider/bidengine/pricing_test.go
```diff
@@ -0,0 +1,93 @@
+package bidengine
+
+import (
+	"testing"
+
+	"github.com/ovrclk/akash/types"
+	"github.com/ovrclk/akash/types/unit"
+	"github.com/stretchr/testify/assert"
+)
+
+func TestCalculatePriceRange(t *testing.T) {
+
+	tests := []struct {
+		name      string
+		resources []types.ResourceGroup
+		min       uint64
+		max       uint64
+	}{
+		{
+			name: "max-unbound",
+			min:  25600,
+			max:  76800,
+			resources: []types.ResourceGroup{
+				{
+					Unit: types.ResourceUnit{
+						CPU:    100,
+						Memory: 512 * unit.Gi,
+						Disk:   512 * unit.Mi,
+					},
+					Count: 1,
+					Price: 1000000,
+				},
+			},
+		},
+		{
+			name: "max-truncated",
+			min:  25600,
+			max:  25601,
+			resources: []types.ResourceGroup{
+				{
+					Unit: types.ResourceUnit{
+						CPU:    100,
+						Memory: 512 * unit.Gi,
+						Disk:   512 * unit.Mi,
+					},
+					Count: 1,
+					Price: 25601,
+				},
+			},
+		},
+		{
+			name: "min-max-same",
+			min:  25,
+			max:  25,
+			resources: []types.ResourceGroup{
+				{
+					Unit: types.ResourceUnit{
+						CPU:    100,
+						Memory: 512 * unit.Mi,
+						Disk:   512 * unit.Mi,
+					},
+					Count: 1,
+					Price: 25,
+				},
+			},
+		},
+		{
+			name: "pass-by-one",
+			min:  25,
+			max:  26,
+			resources: []types.ResourceGroup{
+				{
+					Unit: types.ResourceUnit{
+						CPU:    100,
+						Memory: 512 * unit.Mi,
+						Disk:   512 * unit.Mi,
+					},
+					Count: 1,
+					Price: 26,
+				},
+			},
+		},
+	}
+
+	for _, test := range tests {
+		rlist := &types.DeploymentGroup{Resources: test.resources}
+
+		min, max := calculatePriceRange(rlist)
+		assert.Equal(t, test.min, min, "%v:min=%v", test.name, min)
+		assert.Equal(t, test.max, max, "%v:max=%v", test.name, max)
+	}
+
+}
```
