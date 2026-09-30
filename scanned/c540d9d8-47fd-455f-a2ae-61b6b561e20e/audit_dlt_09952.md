# [?] [R4R] fix: don't panic on expired auctions in init genesis (#668)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-10-02
Source: https://github.com/Kava-Labs/kava/commit/d15e3a43dd6b8b0c3285d64bdd2e45ba3e8c6fe3
Type: security-commit

## Details
[R4R] fix: don't panic on expired auctions in init genesis (#668)

* fix: close expired auctions in init genesis

* fix: initialize variable

* remove expired auction invarient

## Patch
### x/auction/keeper/invariants.go
```diff
@@ -2,7 +2,6 @@ package keeper
 
 import (
 	"fmt"
-	"time"
 
 	"github.com/cosmos/cosmos-sdk/store/prefix"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -61,15 +60,6 @@ func ValidAuctionInvariant(k Keeper) sdk.Invariant {
 				panic("stored auction type does not fulfill GenesisAuction interface")
 			}
 
-			currentTime := ctx.BlockTime()
-			if !currentTime.Equal(time.Time{}) { // this avoids a simulator bug where app.InitGenesis is called with blockTime=0 instead of the correct time
-				if a.GetEndTime().Before(currentTime) {
-					validationErr = fmt.Errorf("endTime before current block time (%s)", currentTime)
-					invalidAuction = a
-					return true
-				}
-			}
-
 			if err := a.Validate(); err != nil {
 				validationErr = err
 				invalidAuction = a
```
