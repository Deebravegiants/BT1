# [?] Fixed all internal tests but one (rust panic caught)

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/wasmd
Published: 2020-01-16
Source: https://github.com/CosmWasm/wasmd/commit/91895d8c602d0eed7a4b7a715c018ed3dd95c109
Type: security-commit

## Details
Fixed all internal tests but one (rust panic caught)

## Patch
### x/wasm/internal/keeper/keeper_test.go
```diff
@@ -1,6 +1,7 @@
 package keeper
 
 import (
+	"encoding/binary"
 	"encoding/json"
 	"io/ioutil"
 	"os"
@@ -84,9 +85,12 @@ func TestInstantiate(t *testing.T) {
 	contractID, err := keeper.Create(ctx, creator, wasmCode)
 	require.NoError(t, err)
 
+	_, _, bob := keyPubAddr()
+	_, _, fred := keyPubAddr()
+
 	initMsg := InitMsg{
-		Verifier:    "fred",
-		Beneficiary: "bob",
+		Verifier:    fred,
+		Beneficiary: bob,
 	}
 	initMsgBz, err := json.Marshal(initMsg)
 	require.NoError(t, err)
@@ -99,8 +103,7 @@ func TestInstantiate(t *testing.T) {
 	require.Equal(t, "cosmos18vd8fpwxzck93qlwghaj6arh4p7c5n89uzcee5", addr.String())
 
 	gasAfter := ctx.GasMeter().GasConsumed()
-	kvStoreGas := uint64(28757) // calculated by disabling contract gas reduction and running test
-	require.Equal(t, kvStoreGas+288, gasAfter-gasBefore)
+	require.Equal(t, uint64(36698), gasAfter-gasBefore)
 }
 
 func TestInstantiateWithNonExistingCodeID(t *testing.T) {
@@ -143,8 +146,8 @@ func TestExecute(t *testing.T) {
 
 	_, _, bob := keyPubAddr()
 	initMsg := InitMsg{
-		Verifier:    fred.String(),
-		Beneficiary: bob.String(),
+		Verifier:    fred,
+		Beneficiary: bob,
 	}
 	initMsgBz, err := json.Marshal(initMsg)
 	require.NoError(t, err)
@@ -182,12 +185,11 @@ func TestExecute(t *testing.T) {
 	diff := time.Now().Sub(start)
 	require.NoError(t, err)
 	require.NotNil(t, res)
-	assert.Equal(t, uint64(81778), res.GasUsed)
+	assert.Equal(t, uint64(118673), res.GasUsed)
 
 	// make sure gas is properly deducted from ctx
 	gasAfter := ctx.GasMeter().GasConsumed()
-	kvStoreGas := uint64(30321) // calculated by disabling contract gas reduction and running test
-	require.Equal(t, kvStoreGas+814, gasAfter-gasBefore)
+	require.Equal(t, uint64(31714), gasAfter-gasBefore)
 
 	// ensure bob now exists and got both payments released
 	bobAcct = accKeeper.GetAccount(ctx, bob)
@@ -219,8 +221,8 @@ func TestExecuteWithNonExistingAddress(t *testing.T) {
 }
 
 type InitMsg struct {
-	Verifier    string `json:"verifier"`
-	Beneficiary string `json:"beneficiary"`
+	Verifier    sdk.AccAddress `json:"verifier"`
+	Beneficiary sdk.AccAddress `json:"beneficiary"`
 }
 
 func createFakeFundedAccount(ctx sdk.Context, am auth.AccountKeeper, coins sdk.Coins) sdk.AccAddress {
@@ -232,8 +234,16 @@ func createFakeFundedAccount(ctx sdk.Context, am auth.AccountKeeper, coins sdk.C
 	return addr
 }
 
+var keyCounter uint64 = 0
+
+// we need to make this deterministic (same every test run), as encoded address size and thus gas cost,
+// depends on the actual bytes (due to ugly CanonicalAddress encoding)
 func keyPubAddr() (crypto.PrivKey, crypto.PubKey, sdk.AccAddress) {
-	key := ed25519.GenPrivKey()
+	keyCounter++
+	seed := make([]byte, 8)
+	binary.BigEndian.PutUint64(seed, keyCounter)
+
+	key := ed25519.GenPrivKeyFromSecret(seed)
 	pub := key.PubKey()
 	addr := sdk.AccAddress(pub.Address())
 	return key, pub, addr
```

### x/wasm/internal/keeper/querier_test.go
```diff
@@ -37,8 +37,8 @@ func TestQueryContractState(t *testing.T) {
 
 	_, _, bob := keyPubAddr()
 	initMsg := InitMsg{
-		Verifier:    anyAddr.String(),
-		Beneficiary: bob.String(),
+		Verifier:    anyAddr,
+		Beneficiary: bob,
 	}
 	initMsgBz, err := json.Marshal(initMsg)
 	require.NoError(t, err)
@@ -114,7 +114,8 @@ func TestQueryContractState(t *testing.T) {
 	for msg, spec := range specs {
 		t.Run(msg, func(t *testing.T) {
 			binResult, err := q(ctx, spec.srcPath, spec.srcReq)
-			require.Equal(t, spec.expErr, err)
+			require.Equal(t, spec.expErr, err, "foo")
+			// require.Equal(t, spec.expErr, err, err.Error())
 			// then
 			var r []model
 			if spec.expErr == nil {
```
