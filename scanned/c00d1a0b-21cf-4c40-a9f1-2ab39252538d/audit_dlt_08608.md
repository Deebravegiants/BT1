# [?] sealing pipeline: Fix panic on padding pieces in WaitDeals (#11708)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-03-12
Source: https://github.com/filecoin-project/lotus/commit/81e65dba5676a93d077d0d420e56eeb9f9a0d27f
Type: security-commit

## Details
sealing pipeline: Fix panic on padding pieces in WaitDeals (#11708)

* sealing pipeline: Fix panic on padding pieces in WaitDeals

* sealing pipeline: Catch panics

## Patch
### storage/pipeline/fsm.go
```diff
@@ -11,6 +11,7 @@ import (
 	"net/http"
 	"os"
 	"reflect"
+	"runtime"
 	"time"
 
 	"golang.org/x/xerrors"
@@ -39,8 +40,27 @@ func (m *Sealing) Plan(events []statemachine.Event, user interface{}) (interface
 		return nil, processed, nil
 	}
 
-	return func(ctx statemachine.Context, si SectorInfo) error {
-		err := next(ctx, si)
+	return func(ctx statemachine.Context, si SectorInfo) (err error) {
+		// handle panics
+		defer func() {
+			if r := recover(); r != nil {
+				buf := make([]byte, 1<<16)
+				n := runtime.Stack(buf, false)
+				buf = buf[:n]
+
+				l := Log{
+					Timestamp: uint64(time.Now().Unix()),
+					Message:   fmt.Sprintf("panic: %v\n%s", r, buf),
+					Kind:      "panic",
+				}
+				si.logAppend(l)
+
+				err = fmt.Errorf("panic: %v\n%s", r, buf)
+			}
+		}()
+
+		// execute the next state
+		err = next(ctx, si)
 		if err != nil {
 			log.Errorf("unhandled sector error (%d): %+v", si.SectorNumber, err)
 			return nil
```

### storage/pipeline/input.go
```diff
@@ -34,12 +34,16 @@ func (m *Sealing) handleWaitDeals(ctx statemachine.Context, sector SectorInfo) e
 	for _, piece := range sector.Pieces {
 		used += piece.Piece().Size.Unpadded()
 
+		if !piece.HasDealInfo() {
+			continue
+		}
+
 		endEpoch, err := piece.EndEpoch()
 		if err != nil {
 			return xerrors.Errorf("piece.EndEpoch: %w", err)
 		}
 
-		if piece.HasDealInfo() && endEpoch > lastDealEnd {
+		if endEpoch > lastDealEnd {
 			lastDealEnd = endEpoch
 		}
 	}
```

### storage/pipeline/types.go
```diff
@@ -289,10 +289,18 @@ func (sp *SafeSectorPiece) handleDealInfo(params handleDealInfoParams) error {
 // SectorPiece Proxy
 
 func (sp *SafeSectorPiece) Impl() piece.PieceDealInfo {
+	if !sp.HasDealInfo() {
+		return piece.PieceDealInfo{}
+	}
+
 	return sp.real.DealInfo.Impl()
 }
 
 func (sp *SafeSectorPiece) String() string {
+	if !sp.HasDealInfo() {
+		return "<no deal info>"
+	}
+
 	return sp.real.DealInfo.String()
 }
 
@@ -305,21 +313,41 @@ func (sp *SafeSectorPiece) Valid(nv network.Version) error {
 }
 
 func (sp *SafeSectorPiece) StartEpoch() (abi.ChainEpoch, error) {
+	if !sp.HasDealInfo() {
+		return 0, xerrors.Errorf("no deal info")
+	}
+
 	return sp.real.DealInfo.StartEpoch()
 }
 
 func (sp *SafeSectorPiece) EndEpoch() (abi.ChainEpoch, error) {
+	if !sp.HasDealInfo() {
+		return 0, xerrors.Errorf("no deal info")
+	}
+
 	return sp.real.DealInfo.EndEpoch()
 }
 
 func (sp *SafeSectorPiece) PieceCID() cid.Cid {
+	if !sp.HasDealInfo() {
+		return sp.real.Piece.PieceCID
+	}
+
 	return sp.real.DealInfo.PieceCID()
 }
 
 func (sp *SafeSectorPiece) KeepUnsealedRequested() bool {
+	if !sp.HasDealInfo() {
+		return false
+	}
+
 	return sp.real.DealInfo.KeepUnsealedRequested()
 }
 
 func (sp *SafeSectorPiece) GetAllocation(ctx context.Context, aapi piece.AllocationAPI, tsk types.TipSetKey) (*verifreg.Allocation, error) {
+	if !sp.HasDealInfo() {
+		return nil, xerrors.Errorf("no deal info")
+	}
+
 	return sp.real.DealInfo.GetAllocation(ctx, aapi, tsk)
 }
```
