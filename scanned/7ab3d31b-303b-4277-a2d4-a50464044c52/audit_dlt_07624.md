# [?] internal/ethapi: fix panic in access list creation (#23133)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-06-30
Source: https://github.com/ethereum/go-ethereum/commit/e7c86936359db6b88571a5fb40496e4ffafdcda5
Type: security-commit

## Details
internal/ethapi: fix panic in access list creation (#23133)

Fixes test failure in the last commit.

## Patch
### ethclient/gethclient/gethclient_test.go
```diff
@@ -40,7 +40,7 @@ import (
 var (
 	testKey, _  = crypto.HexToECDSA("b71c71a67e1177ad4e901695e1b4b9ee17ae16c6668d313eac2f96dbcda3f291")
 	testAddr    = crypto.PubkeyToAddress(testKey.PublicKey)
-	testBalance = big.NewInt(2e10)
+	testBalance = big.NewInt(2e15)
 )
 
 func newTestBackend(t *testing.T) (*node.Node, []*types.Block) {
@@ -88,7 +88,7 @@ func generateTestChain() (*core.Genesis, []*types.Block) {
 	return genesis, blocks
 }
 
-func TestEthClient(t *testing.T) {
+func TestGethClient(t *testing.T) {
 	backend, _ := newTestBackend(t)
 	client, err := backend.Attach()
 	if err != nil {
@@ -159,7 +159,7 @@ func testAccessList(t *testing.T, client *rpc.Client) {
 		From:     testAddr,
 		To:       nil,
 		Gas:      100000,
-		GasPrice: big.NewInt(1),
+		GasPrice: big.NewInt(1000000000),
 		Value:    big.NewInt(1),
 		Data:     common.FromHex("0x608060806080608155fd"),
 	}
@@ -286,7 +286,7 @@ func testCallContract(t *testing.T, client *rpc.Client) {
 		From:     testAddr,
 		To:       &common.Address{},
 		Gas:      21000,
-		GasPrice: big.NewInt(1),
+		GasPrice: big.NewInt(1000000000),
 		Value:    big.NewInt(1),
 	}
 	// CallContract without override
```

### internal/ethapi/api.go
```diff
@@ -1417,11 +1417,11 @@ func AccessList(ctx context.Context, b Backend, blockNrOrHash rpc.BlockNumberOrH
 		}
 		// Copy the original db so we don't modify it
 		statedb := db.Copy()
-		msg := types.NewMessage(args.from(), args.To, uint64(*args.Nonce), args.Value.ToInt(), uint64(*args.Gas), args.GasPrice.ToInt(), nil, nil, args.data(), accessList, false)
+		msg := types.NewMessage(args.from(), args.To, uint64(*args.Nonce), args.Value.ToInt(), uint64(*args.Gas), args.GasPrice.ToInt(), big.NewInt(0), big.NewInt(0), args.data(), accessList, false)
 
 		// Apply the transaction with the access list tracer
 		tracer := vm.NewAccessListTracer(accessList, args.from(), to, precompiles)
-		config := vm.Config{Tracer: tracer, Debug: true}
+		config := vm.Config{Tracer: tracer, Debug: true, NoBaseFee: true}
 		vmenv, _, err := b.GetEVM(ctx, msg, statedb, header, &config)
 		if err != nil {
 			return nil, 0, nil, err
```
