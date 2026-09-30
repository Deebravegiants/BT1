# [?] fixed non-deterministic terra dev environment items

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-09-07
Source: https://github.com/wormhole-foundation/wormhole/commit/a79ef81721fdded3abc3844900a8a0748ac02ae6
Type: security-commit

## Details
fixed non-deterministic terra dev environment items

Change-Id: Ie97c43a4f6fb562e9b546793d216a1be2ba302eb

## Patch
### bridge_ui/src/components/TokenSelectors/TerraSourceTokenSelector.tsx
```diff
@@ -167,6 +167,7 @@ export default function TerraSourceTokenSelector(
 
   const toggleAdvancedMode = () => {
     setAdvancedMode(!advancedMode);
+    setAdvancedModeError("");
   };
 
   const advancedModeToggleButton = (
```

### bridge_ui/src/utils/consts.ts
```diff
@@ -111,8 +111,7 @@ export const TERRA_TEST_TOKEN_ADDRESS =
 export const TERRA_BRIDGE_ADDRESS =
   "terra18vd8fpwxzck93qlwghaj6arh4p7c5n896xzem5";
 export const TERRA_TOKEN_BRIDGE_ADDRESS =
-  "terra174kgn5rtw4kf6f938wm7kwh70h2v4vcfd26jlc";
-// "terra10pyejy66429refv3g35g2t7am0was7ya7kz2a4";
+  "terra10pyejy66429refv3g35g2t7am0was7ya7kz2a4";
 
 export const COVALENT_API_KEY = process.env.REACT_APP_COVALENT_API_KEY
   ? process.env.REACT_APP_COVALENT_API_KEY
```

### devnet/node.yaml
```diff
@@ -87,7 +87,7 @@ spec:
             - --terraChainID
             - localterra
             - --terraContract
-            - terra18eezxhys9jwku67cm4w84xhnzt4xjj77w2qt62
+            - terra18vd8fpwxzck93qlwghaj6arh4p7c5n896xzem5
             - --solanaContract
             - Bridge1p5gheXUvJ6jGWGeCsgPKgnE3YgdGKRVCMY9o
             - --solanaWS
```

### sdk/js/src/bridge/getEmitterAddress.ts
```diff
@@ -1,4 +1,5 @@
 import { PublicKey } from "@solana/web3.js";
+import { bech32 } from "bech32";
 import { arrayify, BytesLike, Hexable, zeroPad } from "ethers/lib/utils";
 
 export function getEmitterAddressEth(
@@ -15,7 +16,7 @@ export async function getEmitterAddressSolana(programAddress: string) {
 }
 
 export async function getEmitterAddressTerra(programAddress: string) {
-  // Testnet Hardcoded
-  // TODO: HumanAddr -> CanonicalAddr
-  return "000000000000000000000000784999135aaa8a3ca5914468852fdddbddd8789d";
+  return Buffer.from(
+    zeroPad(bech32.fromWords(bech32.decode(programAddress).words), 32)
+  ).toString("hex");
 }
```

### terra/tools/deploy.py
```diff
@@ -78,8 +78,9 @@ async def store_contract(contract_name):
 async def store_contracts():
     parent_dir = os.path.dirname(__file__)
     contract_names = [
-        i[:-5] for i in os.listdir(f"{parent_dir}/../artifacts") if i.endswith(".wasm")
+        i[:-5] for i in sorted(os.listdir(f"{parent_dir}/../artifacts"), reverse = True) if i.endswith(".wasm")
     ]
+    
 
     return {
         contract_name: await store_contract(contract_name)
```
