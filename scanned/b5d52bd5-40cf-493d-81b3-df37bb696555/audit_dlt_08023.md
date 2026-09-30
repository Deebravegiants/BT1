# [?] core: Fix panic with the tx pool

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-24
Source: https://github.com/celo-org/celo-blockchain/commit/aea4a8584fcc63804ba8ae7ff0f7a501760dd366
Type: security-commit

## Details
core: Fix panic with the tx pool

## Patch
### core/tx_list.go
```diff
@@ -751,12 +751,14 @@ func newTxPricedList(all *txLookup, ctx *atomic.Value) *txPricedList {
 		ctx: ctx,
 		all: all,
 		urgent: multiCurrencyPriceHeap{
-			currencyCmpFn:   txCtx.CmpValues,
-			nilCurrencyHeap: &priceHeap{},
+			currencyCmpFn:       txCtx.CmpValues,
+			nilCurrencyHeap:     &priceHeap{},
+			nonNilCurrencyHeaps: make(map[common.Address]*priceHeap),
 		},
 		floating: multiCurrencyPriceHeap{
-			currencyCmpFn:   txCtx.CmpValues,
-			nilCurrencyHeap: &priceHeap{},
+			currencyCmpFn:       txCtx.CmpValues,
+			nilCurrencyHeap:     &priceHeap{},
+			nonNilCurrencyHeaps: make(map[common.Address]*priceHeap),
 		},
 	}
 }
```
