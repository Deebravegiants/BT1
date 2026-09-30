# [?] Fix data race in tests (#6877)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-11-14
Source: https://github.com/osmosis-labs/osmosis/commit/00c6d2229c5d046ef31b2ab649f64cb6c4fac519
Type: security-commit

## Details
Fix data race in tests (#6877)

## Patch
### x/txfees/keeper/mempool-1559/code.go
```diff
@@ -4,6 +4,7 @@ import (
 	"encoding/json"
 	"fmt"
 	"os"
+	"sync"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 
@@ -95,6 +96,11 @@ func (e *EipState) startBlock(height int64) {
 	}
 }
 
+func (e EipState) Clone() EipState {
+	e.CurBaseFee = e.CurBaseFee.Clone()
+	return e
+}
+
 // deliverTxCode runs on every transaction in the feedecorator ante handler and sums the gas of each transaction
 func (e *EipState) deliverTxCode(ctx sdk.Context, tx sdk.FeeTx) {
 	if ctx.BlockHeight() != e.lastBlockHeight {
@@ -133,7 +139,7 @@ func (e *EipState) updateBaseFee(height int64) {
 		e.CurBaseFee = MaxBaseFee.Clone()
 	}
 
-	go e.tryPersist()
+	go e.Clone().tryPersist()
 }
 
 // GetCurBaseFee returns a clone of the CurBaseFee to avoid overwriting the initial value in
@@ -148,9 +154,13 @@ func (e *EipState) GetCurRecheckBaseFee() osmomath.Dec {
 	return e.CurBaseFee.Clone().Quo(sdk.NewDec(RecheckFeeConstant))
 }
 
+var rwMtx = sync.Mutex{}
+
 // tryPersist persists the eip1559 state to disk in the form of a json file
 // we do this in case a node stops and it can continue functioning as normal
-func (e *EipState) tryPersist() {
+func (e EipState) tryPersist() {
+	rwMtx.Lock()
+	defer rwMtx.Unlock()
 	bz, err := json.Marshal(e)
 	if err != nil {
 		fmt.Println("Error marshalling eip1559 state", err)
@@ -167,6 +177,8 @@ func (e *EipState) tryPersist() {
 // tryLoad reads eip1559 state from disk and initializes the CurEipState to
 // the previous state when a node is restarted
 func (e *EipState) tryLoad() osmomath.Dec {
+	rwMtx.Lock()
+	defer rwMtx.Unlock()
 	bz, err := os.ReadFile(e.BackupFilePath)
 	if err != nil {
 		fmt.Println("Error reading eip1559 state", err)
```
