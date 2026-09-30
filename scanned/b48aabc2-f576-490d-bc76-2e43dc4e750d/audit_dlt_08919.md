# [?] near/dust: Fix dust underflow

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-09-12
Source: https://github.com/wormhole-foundation/wormhole/commit/3288b0abb7322b64af869ccde9e7a773c2ed6013
Type: security-commit

## Details
near/dust: Fix dust underflow

## Patch
### near/contracts/token-bridge/src/lib.rs
```diff
@@ -993,7 +993,7 @@ impl TokenBridge {
             env::panic_str("transfer exceeds max bridged token amount");
         }
 
-        let dust = amount - (namount * NEAR_MULT) - (nfee * NEAR_MULT);
+        let dust = amount - (namount * NEAR_MULT);
 
         let mut p = [
             // PayloadID uint8 = 1
```

### sdk/js/src/token_bridge/attest.ts
```diff
@@ -248,7 +248,7 @@ export async function attestTokenFromNear(
     contractId: tokenBridge,
     methodName: "attest_token",
     args: { token: asset, message_fee: message_fee },
-    attachedDeposit: new BN("3000000000000000000000") + new BN(message_fee), // 0.003 NEAR
+    attachedDeposit: new BN("3000000000000000000000").add(new BN(message_fee)), // 0.003 NEAR
     gas: new BN("100000000000000"),
   });
 
```

### sdk/js/src/token_bridge/transfer.ts
```diff
@@ -771,11 +771,11 @@ export async function transferNearFromNear(
     args: {
       receiver: uint8ArrayToHex(receiver),
       chain: chain,
-      fee: fee.toString(10),
+      fee: fee.toString(),
       payload: payload,
       message_fee: message_fee,
     },
-    attachedDeposit: (new BN(qty.toString(10)) + new BN(message_fee)),
+    attachedDeposit: (new BN(qty.toString()).add(new BN(message_fee))),
     gas: new BN("100000000000000"),
   });
 
```
