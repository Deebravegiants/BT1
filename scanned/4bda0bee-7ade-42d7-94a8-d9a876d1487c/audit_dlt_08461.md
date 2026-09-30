# [?] fix(header/store): ensure hieghtSub does not panic on Pub when empty slice is given

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2022-06-01
Source: https://github.com/celestiaorg/celestia-node/commit/7d6297703b22fdeb2e0724d95fea1eb3b8b24de9
Type: security-commit

## Details
fix(header/store): ensure hieghtSub does not panic on Pub when empty slice is given

## Patch
### header/store/heightsub.go
```diff
@@ -3,7 +3,6 @@ package store
 import (
 	"context"
 	"errors"
-
 	"sync"
 	"sync/atomic"
 
@@ -72,8 +71,13 @@ func (hs *heightSub) Sub(ctx context.Context, height uint64) (*header.ExtendedHe
 // For Pub to work correctly, heightSub has to be initialized with SetHeight
 // so that given headers are contiguous to the height on heightSub.
 func (hs *heightSub) Pub(headers ...*header.ExtendedHeader) {
+	ln := len(headers)
+	if ln == 0 {
+		return
+	}
+
 	height := hs.Height()
-	from, to := uint64(headers[0].Height), uint64(headers[len(headers)-1].Height)
+	from, to := uint64(headers[0].Height), uint64(headers[ln-1].Height)
 	if height+1 != from {
 		log.Fatal("PLEASE FILE A BUG REPORT: headers given to the heightSub are in the wrong order")
 		return
@@ -86,7 +90,7 @@ func (hs *heightSub) Pub(headers ...*header.ExtendedHeader) {
 	// there is a common case where we Pub only header
 	// in this case, we shouldn't loop over each heightReqs
 	// and instead read from the map directly
-	if len(headers) == 1 {
+	if ln == 1 {
 		reqs, ok := hs.heightReqs[from]
 		if ok {
 			for _, req := range reqs {
```
