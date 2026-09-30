# [?] Avoid panic tx error message in debug trace (#2057)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-01-27
Source: https://github.com/sei-protocol/sei-chain/commit/bc47cc90f8371e70eab6a1482d9d1679e4bcf4cb
Type: security-commit

## Details
Avoid panic tx error message in debug trace (#2057)

* checkpoint

* fix

* fix

## Patch
### contracts/test/EVMPrecompileTest.js
```diff
@@ -4,7 +4,7 @@ const fs = require('fs');
 const path = require('path');
 
 const { expectRevert } = require('@openzeppelin/test-helpers');
-const { setupSigners, getAdmin, deployWasm, storeWasm, execute, isDocker, ABI, createTokenFactoryTokenAndMint, getSeiBalance} = require("./lib");
+const { setupSigners, getAdmin, deployWasm, storeWasm, execute, isDocker, ABI, createTokenFactoryTokenAndMint, getSeiBalance, rawHttpDebugTraceWithCallTracer} = require("./lib");
 
 
 describe("EVM Precompile Tester", function () {
@@ -17,6 +17,32 @@ describe("EVM Precompile Tester", function () {
         admin = await getAdmin();
     })
 
+    describe("EVM Bank Precompile Tester", function () {
+        const BankPrecompileContract = '0x0000000000000000000000000000000000001001';
+        let bank;
+
+        before(async function () {
+            const signer = accounts[0].signer
+            const contractABIPath = '../../precompiles/bank/abi.json';
+            const contractABI = require(contractABIPath);
+            // Get a contract instance
+            bank = new ethers.Contract(BankPrecompileContract, contractABI, signer);
+        });
+
+        it("Fails with 'execution reverted' not 'panic occurred' when insufficient gas is provided", async function () {
+            try {
+                const bankSendTx = await bank.sendNative(accounts[1].seiAddress, {value: 1, gasLimit: 40000});
+                await bankSendTx.wait();
+            } catch (error) {
+                const txHash = error.receipt.hash
+                // should not get "panic occurred"
+                const trace = await rawHttpDebugTraceWithCallTracer(txHash)
+                expect(trace.result.error).to.not.include("panic")
+                expect(trace.result.error).to.include("execution reverted")
+            }
+        });
+    });
+
     describe("EVM Addr Precompile Tester", function () {
         const AddrPrecompileContract = '0x0000000000000000000000000000000000001004';
         let addr;
@@ -72,6 +98,22 @@ describe("EVM Precompile Tester", function () {
             const seiAddr = await addr.getSeiAddr(unassociatedWallet.address);
             expect(seiAddr).to.not.be.null;
         });
+
+        it("Fails with 'execution reverted' not 'panic occurred' when insufficient gas is provided", async function () {
+            const unassociatedWallet = hre.ethers.Wallet.createRandom();
+            try {
+                // provide less than gas than needed to execute the transaction
+                const associatedAddrs = await addr.associatePubKey(unassociatedWallet.publicKey.slice(2), {gasLimit: 52000});
+                await associatedAddrs.wait();
+                expect.fail("Expected an error here since we provided insufficient gas");
+            } catch (error) {
+                const txHash = error.receipt.hash
+                // should not get "panic occurred"
+                const trace = await rawHttpDebugTraceWithCallTracer(txHash)
+                expect(trace.result.error).to.not.include("panic");
+                expect(trace.result.error).to.include("execution reverted");
+            }
+        });
     });
 
     describe("EVM Gov Precompile Tester", function () {
```

### contracts/test/lib.js
```diff
@@ -1,5 +1,6 @@
 const { exec } = require("child_process");
 const {ethers} = require("hardhat"); // Importing exec from child_process
+const axios = require("axios");
 
 const adminKeyName = "admin"
 
@@ -198,6 +199,19 @@ async function incrementPointerVersion(provider, pointerType, offset) {
     }
 }
 
+async function rawHttpDebugTraceWithCallTracer(txHash) {
+    const payload = {
+        jsonrpc: "2.0",
+        method: "debug_traceTransaction",
+        params: [txHash, {"tracer": "callTracer"}], // The second parameter is an optional trace config object
+        id: 1,
+    };
+    const response = await axios.post("http://localhost:8545", payload, {
+        headers: { "Content-Type": "application/json" },
+    });
+    return response.data;
+}
+
 async function createTokenFactoryTokenAndMint(name, amount, recipient, from=adminKeyName) {
     const command = `seid tx tokenfactory create-denom ${name} --from ${from} --gas=5000000 --fees=1000000usei -y --broadcast-mode block -o json`
     const output = await execute(command);
@@ -211,6 +225,28 @@ async function createTokenFactoryTokenAndMint(name, amount, recipient, from=admi
     return token_denom
 }
 
+async function getChainId() {
+    const nodeUrl = 'http://localhost:8545';
+    const response = await axios.post(nodeUrl, {
+        method: 'eth_chainId',
+        params: [],
+        id: 1,
+        jsonrpc: "2.0"
+    })
+    return response.data.result;
+}
+
+async function getGasPrice() {
+    const nodeUrl = 'http://localhost:8545';
+    const response = await axios.post(nodeUrl, {
+        method: 'eth_gasPrice',
+        params: [],
+        id: 1,
+        jsonrpc: "2.0"
+    })
+    return response.data.result;
+}
+
 async function getPointerForNative(name) {
     const command = `seid query evm pointer NATIVE ${name} -o json`
     const output = await execute(command);
@@ -526,10 +562,13 @@ module.exports = {
     deployWasm,
     instantiateWasm,
     createTokenFactoryTokenAndMint,
+    getChainId,
+    getGasPrice,
     execute,
     getSeiAddress,
     getEvmAddress,
     queryWasm,
+    rawHttpDebugTraceWithCallTracer,
     executeWasm,
     getAdmin,
     setupSigners,
```

### precompiles/addr/addr.go
```diff
@@ -89,6 +89,12 @@ func (p PrecompileExecutor) RequiredGas(input []byte, method *abi.Method) uint64
 }
 
 func (p PrecompileExecutor) Execute(ctx sdk.Context, method *abi.Method, _ common.Address, _ common.Address, args []interface{}, value *big.Int, readOnly bool, _ *vm.EVM, suppliedGas uint64) (ret []byte, remainingGas uint64, err error) {
+	// Needed to catch gas meter panics
+	defer func() {
+		if r := recover(); r != nil {
+			err = fmt.Errorf("execution reverted: %v", r)
+		}
+	}()
 	switch method.Name {
 	case GetSeiAddressMethod:
 		return p.getSeiAddr(ctx, method, args, value)
```

### precompiles/addr/addr_test.go
```diff
@@ -45,11 +45,12 @@ func TestAssociatePubKey(t *testing.T) {
 	happyPathOutput, _ := associatePubKey.Outputs.Pack(targetSeiAddress.String(), targetEvmAddress)
 
 	type args struct {
-		evm      *vm.EVM
-		caller   common.Address
-		pubKey   string
-		value    *big.Int
-		readOnly bool
+		evm         *vm.EVM
+		caller      common.Address
+		pubKey      string
+		value       *big.Int
+		readOnly    bool
+		suppliedGas uint64
 	}
 	tests := []struct {
 		name       string
@@ -116,6 +117,21 @@ func TestAssociatePubKey(t *testing.T) {
 			wantErr:    true,
 			wantErrMsg: fmt.Sprintf("address %s is already associated with evm address %s", callerSeiAddress, callerEvmAddress),
 		},
+		{
+			name: "fails if insufficient gas provided",
+			args: args{
+				evm: &vm.EVM{
+					StateDB:   state.NewDBImpl(ctx, k, true),
+					TxContext: vm.TxContext{Origin: callerEvmAddress},
+				},
+				caller:      callerEvmAddress,
+				pubKey:      targetPubKeyHex,
+				value:       big.NewInt(0),
+				suppliedGas: 1,
+			},
+			wantErr:    true,
+			wantErrMsg: "execution reverted: {ReadFlat}",
+		},
 		{
 			name: "happy path - associates addresses if signature is correct",
 			args: args{
@@ -141,7 +157,11 @@ func TestAssociatePubKey(t *testing.T) {
 			require.Nil(t, err)
 
 			// Make the call to associate.
-			ret, _, err := p.RunAndCalculateGas(tt.args.evm, tt.args.caller, tt.args.caller, append(p.GetExecutor().(*addr.PrecompileExecutor).AssociatePubKeyID, inputs...), 40000, tt.args.value, nil, tt.args.readOnly, false)
+			suppliedGas := uint64(40000)
+			if tt.args.suppliedGas != 0 {
+				suppliedGas = tt.args.suppliedGas
+			}
+			ret, _, err := p.RunAndCalculateGas(tt.args.evm, tt.args.caller, tt.args.caller, append(p.GetExecutor().(*addr.PrecompileExecutor).AssociatePubKeyID, inputs...), suppliedGas, tt.args.value, nil, tt.args.readOnly, false)
 			if (err != nil) != tt.wantErr {
 				t.Errorf("Run() error = %v, wantErr %v %v", err, tt.wantErr, string(ret))
 				return
```

### precompiles/bank/bank.go
```diff
@@ -103,6 +103,12 @@ func (p PrecompileExecutor) RequiredGas(input []byte, method *abi.Method) uint64
 }
 
 func (p PrecompileExecutor) Execute(ctx sdk.Context, method *abi.Method, caller common.Address, callingContract common.Address, args []interface{}, value *big.Int, readOnly bool, evm *vm.EVM, suppliedGas uint64) (ret []byte, remainingGas uint64, err error) {
+	// Needed to catch gas meter panics
+	defer func() {
+		if r := recover(); r != nil {
+			err = fmt.Errorf("execution reverted: %v", r)
+		}
+	}()
 	switch method.Name {
 	case SendMethod:
 		return p.send(ctx, caller, method, args, value, readOnly)
```

### precompiles/oracle/oracle.go
```diff
@@ -2,6 +2,7 @@ package oracle
 
 import (
 	"embed"
+	"fmt"
 	"math/big"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -79,6 +80,12 @@ func (p PrecompileExecutor) RequiredGas(input []byte, method *abi.Method) uint64
 }
 
 func (p PrecompileExecutor) Execute(ctx sdk.Context, method *abi.Method, caller common.Address, callingContract common.Address, args []interface{}, value *big.Int, readOnly bool, evm *vm.EVM, suppliedGas uint64) (bz []byte, remainingGas uint64, err error) {
+	// Needed to catch gas meter panics
+	defer func() {
+		if r := recover(); r != nil {
+			err = fmt.Errorf("execution reverted: %v", r)
+		}
+	}()
 	switch method.Name {
 	case GetExchangeRatesMethod:
 		return p.getExchangeRates(ctx, method, args, value)
```
