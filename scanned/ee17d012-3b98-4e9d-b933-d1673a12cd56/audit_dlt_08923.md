# [?] bridge_ui: fix crash in solana token picker

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-09-23
Source: https://github.com/wormhole-foundation/wormhole/commit/66d75c97a33ed78161cc8ca313dcef2f9d26498d
Type: security-commit

## Details
bridge_ui: fix crash in solana token picker

Change-Id: I27f7b2b380a5f1a9dcd48468bc011b5e17e630db

## Patch
### bridge_ui/src/components/TokenSelectors/SolanaSourceTokenSelector.tsx
```diff
@@ -8,6 +8,7 @@ import React, { useCallback, useMemo } from "react";
 import useMetaplexData from "../../hooks/useMetaplexData";
 import useSolanaTokenMap from "../../hooks/useSolanaTokenMap";
 import { DataWrapper } from "../../store/helpers";
+import { NFTParsedTokenAccount } from "../../store/nftSlice";
 import { ParsedTokenAccount } from "../../store/transferSlice";
 import {
   MIGRATION_ASSET_MAP,
@@ -34,7 +35,7 @@ const useStyles = makeStyles((theme: Theme) =>
 
 type SolanaSourceTokenSelectorProps = {
   value: ParsedTokenAccount | null;
-  onChange: (newValue: ParsedTokenAccount | null) => void;
+  onChange: (newValue: NFTParsedTokenAccount | null) => void;
   accounts: ParsedTokenAccount[];
   disabled: boolean;
   mintAccounts:
@@ -263,11 +264,16 @@ export default function SolanaSourceTokenSelector(
   }, [isWormholev1, isMigrationEligible]);
 
   const onAutocompleteChange = useCallback(
-    (event, newValue) => {
+    (event, newValue: NFTParsedTokenAccount | null) => {
+      if (!newValue) {
+        onChange(null);
+        return;
+      }
       const symbol = getSymbol(newValue);
       const name = getName(newValue);
       const logo = getLogo(newValue);
       // TODO: more nft data
+
       onChange({
         ...newValue,
         symbol,
```
