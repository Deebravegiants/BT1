# [?] fix: fixing panic on GetShare with out of bounds indexes (#2605)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-08-29
Source: https://github.com/celestiaorg/celestia-node/commit/8deffba77b0e68f6a2229bc8266359eda704c584
Type: security-commit

## Details
fix: fixing panic on GetShare with out of bounds indexes (#2605)

GetShare would panic on RPC calls if the passed indicies were out of
bounds.

## Patch
### share/getter.go
```diff
@@ -13,6 +13,8 @@ import (
 var (
 	// ErrNotFound is used to indicate that requested data could not be found.
 	ErrNotFound = errors.New("share: data not found")
+	// ErrOutOfBounds is used to indicate that a passed row or column index is out of bounds of the square size.
+	ErrOutOfBounds = errors.New("share: row or column index is larger than square size")
 )
 
 // Getter interface provides a set of accessors for shares by the Root.
```

### share/getters/cascade.go
```diff
@@ -3,7 +3,6 @@ package getters
 import (
 	"context"
 	"errors"
-	"fmt"
 
 	"go.opentelemetry.io/otel/attribute"
 	"go.opentelemetry.io/otel/trace"
@@ -38,9 +37,10 @@ func (cg *CascadeGetter) GetShare(ctx context.Context, root *share.Root, row, co
 		attribute.Int("col", col),
 	))
 	defer span.End()
-	if row >= len(root.RowRoots) || col >= len(root.ColumnRoots) {
-		err := fmt.Errorf("cascade/get-share: invalid indexes were provided:rowIndex=%d, colIndex=%d."+
-			"squarewidth=%d", row, col, len(root.RowRoots))
+
+	upperBound := len(root.RowRoots)
+	if row >= upperBound || col >= upperBound {
+		err := share.ErrOutOfBounds
 		span.RecordError(err)
 		return nil, err
 	}
```

### share/getters/getter_test.go
```diff
@@ -107,6 +107,10 @@ func TestStoreGetter(t *testing.T) {
 			}
 		}
 
+		// doesn't panic on indexes too high
+		_, err := sg.GetShare(ctx, &dah, squareSize, squareSize)
+		require.ErrorIs(t, err, share.ErrOutOfBounds)
+
 		// root not found
 		_, dah = randomEDS(t)
 		_, err = sg.GetShare(ctx, &dah, 0, 0)
@@ -184,6 +188,10 @@ func TestIPLDGetter(t *testing.T) {
 			}
 		}
 
+		// doesn't panic on indexes too high
+		_, err := sg.GetShare(ctx, &dah, squareSize+1, squareSize+1)
+		require.ErrorIs(t, err, share.ErrOutOfBounds)
+
 		// root not found
 		_, dah = randomEDS(t)
 		_, err = sg.GetShare(ctx, &dah, 0, 0)
```

### share/getters/ipld.go
```diff
@@ -48,6 +48,12 @@ func (ig *IPLDGetter) GetShare(ctx context.Context, dah *share.Root, row, col in
 		utils.SetStatusAndEnd(span, err)
 	}()
 
+	upperBound := len(dah.RowRoots)
+	if row >= upperBound || col >= upperBound {
+		err := share.ErrOutOfBounds
+		span.RecordError(err)
+		return nil, err
+	}
 	root, leaf := ipld.Translate(dah, row, col)
 
 	// wrap the blockservice in a session if it has been signaled in the context.
```

### share/getters/store.go
```diff
@@ -43,6 +43,12 @@ func (sg *StoreGetter) GetShare(ctx context.Context, dah *share.Root, row, col i
 		utils.SetStatusAndEnd(span, err)
 	}()
 
+	upperBound := len(dah.RowRoots)
+	if row >= upperBound || col >= upperBound {
+		err := share.ErrOutOfBounds
+		span.RecordError(err)
+		return nil, err
+	}
 	root, leaf := ipld.Translate(dah, row, col)
 	bs, err := sg.store.CARBlockstore(ctx, dah.Hash())
 	if errors.Is(err, eds.ErrNotFound) {
```
