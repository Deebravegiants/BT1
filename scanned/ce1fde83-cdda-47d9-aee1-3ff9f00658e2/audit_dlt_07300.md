# [?] Guard against overflows in Shelley TxIns

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/cardano-node
Published: 2022-01-07
Source: https://github.com/IntersectMBO/cardano-node/commit/570166771401ef8a45ac5a57fee0eb4825ce682b
Type: security-commit

## Details
Guard against overflows in Shelley TxIns

- makeByronTransactionBody guards against overflows in the transaction indices,
but makeShelleyTransactionBody does not.
- Add appropriate guards to makeShelleyTransactionBody.

## Patch
### cardano-api/src/Cardano/Api/TxBody.hs
```diff
@@ -157,7 +157,7 @@ module Cardano.Api.TxBody (
   ) where
 
 import           Control.Applicative (some)
-import           Control.Monad (guard)
+import           Control.Monad (guard, unless)
 import           Data.Aeson (object, withObject, (.:), (.:?), (.=))
 import qualified Data.Aeson as Aeson
 import qualified Data.Aeson.Key as Aeson
@@ -2463,26 +2463,31 @@ validateTxBodyContent era txBodContent@TxBodyContent {
   in case era of
        ShelleyBasedEraShelley -> do
          validateTxIns txIns
+         guardShelleyTxInsOverflow (map fst txIns)
          validateTxOuts era txOuts
          validateMetadata txMetadata
        ShelleyBasedEraAllegra -> do
          validateTxIns txIns
+         guardShelleyTxInsOverflow (map fst txIns)
          validateTxOuts era txOuts
          validateMetadata txMetadata
        ShelleyBasedEraMary -> do
          validateTxIns txIns
+         guardShelleyTxInsOverflow (map fst txIns)
          validateTxOuts era txOuts
          validateMetadata txMetadata
          validateMintValue txMintValue
        ShelleyBasedEraAlonzo -> do
          validateTxIns txIns
+         guardShelleyTxInsOverflow (map fst txIns)
          validateTxOuts era txOuts
          validateMetadata txMetadata
          validateMintValue txMintValue
          validateTxInsCollateral txInsCollateral languages
          validateProtocolParameters txProtocolParams languages
        ShelleyBasedEraBabbage -> do
          validateTxIns txIns
+         guardShelleyTxInsOverflow (map fst txIns)
          validateTxOuts era txOuts
          validateMetadata txMetadata
          validateMintValue txMintValue
@@ -2524,9 +2529,10 @@ validateTxInsCollateral
   :: TxInsCollateral era -> Set Alonzo.Language -> Either TxBodyError ()
 validateTxInsCollateral txInsCollateral languages =
   case txInsCollateral of
-    TxInsCollateralNone | not (Set.null languages)
-      -> Left TxBodyEmptyTxInsCollateral
-    _ -> return ()
+    TxInsCollateralNone ->
+      unless (Set.null languages) (Left TxBodyEmptyTxInsCollateral)
+    TxInsCollateral _ collateralTxIns ->
+      guardShelleyTxInsOverflow collateralTxIns
 
 validateTxOuts :: ShelleyBasedEra era -> [TxOut CtxTx era] -> Either TxBodyError ()
 validateTxOuts era txOuts =
@@ -3551,6 +3557,11 @@ getLedgerEraConstraint ShelleyBasedEraAlonzo f = f
 getLedgerEraConstraint ShelleyBasedEraBabbage f = f
 getLedgerEraConstraint ShelleyBasedEraConway f = f
 
+guardShelleyTxInsOverflow :: [TxIn] -> Either TxBodyError ()
+guardShelleyTxInsOverflow txIns = do
+    for_ txIns $ \txin@(TxIn _ (TxIx txix)) ->
+      guard (txix <= maxShelleyTxInIx) ?! TxBodyInIxOverflow txin
+
 makeShelleyTransactionBody
   :: ShelleyBasedEra era
   -> TxBodyContent BuildTx era
```
