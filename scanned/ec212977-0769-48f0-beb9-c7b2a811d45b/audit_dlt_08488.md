# [?] Fix store iterator deadlock under high load (#567)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-02-16
Source: https://github.com/sei-protocol/sei-chain/commit/0da9fc6a7230a97509b49d9a4fcccd831177e76e
Type: security-commit

## Details
Fix store iterator deadlock under high load (#567)

Co-authored-by: Yiming Zang <yzang@twitter.com>
Do store writes outside of iterator iteration and after the iterator is closed.

## Patch
### x/dex/cache/order.go
```diff
@@ -58,10 +58,21 @@ func (o *BlockOrders) MarkFailedToPlace(failedOrders []wasm.UnsuccessfulOrder) {
 		failedOrdersMap[failedOrder.ID] = failedOrder
 	}
 
+	keys, vals := o.getKVsToSet(failedOrdersMap)
+	for i, key := range keys {
+		o.orderStore.Set(key, vals[i])
+	}
+}
+
+// getKVsToSet iterate through the kvstore and append the key,val items to a list.
+// We should avoid writing or reading from the store directly within the iterator.
+func (o *BlockOrders) getKVsToSet(failedOrdersMap map[uint64]wasm.UnsuccessfulOrder) ([][]byte, [][]byte) {
 	iterator := sdk.KVStorePrefixIterator(o.orderStore, []byte{})
 
 	defer iterator.Close()
 
+	var keys [][]byte
+	var vals [][]byte
 	for ; iterator.Valid(); iterator.Next() {
 		var val types.Order
 		if err := val.Unmarshal(iterator.Value()); err != nil {
@@ -74,9 +85,11 @@ func (o *BlockOrders) MarkFailedToPlace(failedOrders []wasm.UnsuccessfulOrder) {
 		if bz, err := val.Marshal(); err != nil {
 			panic(err)
 		} else {
-			o.orderStore.Set(iterator.Key(), bz)
+			keys = append(keys, iterator.Key())
+			vals = append(vals, bz)
 		}
 	}
+	return keys, vals
 }
 
 func (o *BlockOrders) GetSortedMarketOrders(direction types.PositionDirection, includeLiquidationOrders bool) []*types.Order {
```
