# [?] internal/ethapi: fix panic in accesslist creation (#23225)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-07-28
Source: https://github.com/celo-org/celo-blockchain/commit/2faf796d2a502ef6d3c02681a649bd3f41999ccc
Type: security-commit

## Details
internal/ethapi: fix panic in accesslist creation (#23225)

* internal/ethapi: revert + fix properly in al tracer

* internal/ethapi: use toMessage instead of creating new message

* internal/ethapi: remove ineffassign

* core: fix invalid unmarshalling, fix test

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### core/vm/access_list_tracer.go
```diff
@@ -96,7 +96,7 @@ func (al accessList) equal(other accessList) bool {
 func (al accessList) accessList() types.AccessList {
 	acl := make(types.AccessList, 0, len(al))
 	for addr, slots := range al {
-		tuple := types.AccessTuple{Address: addr}
+		tuple := types.AccessTuple{Address: addr, StorageKeys: []common.Hash{}}
 		for slot := range slots {
 			tuple.StorageKeys = append(tuple.StorageKeys, slot)
 		}
```

### ethclient/gethclient/gethclient_test.go
```diff
@@ -138,7 +138,7 @@ func testAccessList(t *testing.T, client *rpc.Client) {
 		From:     testAddr,
 		To:       &common.Address{},
 		Gas:      21000,
-		GasPrice: big.NewInt(1),
+		GasPrice: big.NewInt(765625000),
 		Value:    big.NewInt(1),
 	}
 	al, gas, vmErr, err := ec.CreateAccessList(context.Background(), msg)
```

### internal/ethapi/api.go
```diff
@@ -1441,7 +1441,12 @@ func AccessList(ctx context.Context, b Backend, blockNrOrHash rpc.BlockNumberOrH
 		}
 		// Copy the original db so we don't modify it
 		statedb := db.Copy()
-		msg := types.NewMessage(args.from(), args.To, uint64(*args.Nonce), args.Value.ToInt(), uint64(*args.Gas), args.GasPrice.ToInt(), big.NewInt(0), big.NewInt(0), args.data(), accessList, false)
+		// Set the accesslist to the last al
+		args.AccessList = &accessList
+		msg, err := args.ToMessage(b.RPCGasCap(), header.BaseFee)
+		if err != nil {
+			return nil, 0, nil, err
+		}
 
 		// Apply the transaction with the access list tracer
 		tracer := vm.NewAccessListTracer(accessList, args.from(), to, precompiles)
```
