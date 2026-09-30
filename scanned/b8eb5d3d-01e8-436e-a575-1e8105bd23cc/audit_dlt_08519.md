# [?] Merge pull request #5401 from input-output-hk/mgalazyn/fix/fix-node-crash-in-babbage

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/cardano-node
Published: 2023-07-21
Source: https://github.com/IntersectMBO/cardano-node/commit/712b0950ff0e008f8dc06645ee7d56d53f6d8e5d
Type: security-commit

## Details
Merge pull request #5401 from input-output-hk/mgalazyn/fix/fix-node-crash-in-babbage

input-output-hk/cardano-cli#85 Fix node crashing in babbage

## Patch
### cardano-node/src/Cardano/Tracing/OrphanInstances/Shelley.hs
```diff
@@ -134,8 +134,8 @@ instance
   ) => ToObject (ShelleyLedgerError ledgerera) where
   toObject verb (BBodyError (BlockTransitionError fs)) =
     mconcat [ "kind" .= String "BBodyError"
-             , "failures" .= map (toObject verb) fs
-             ]
+            , "failures" .= map (toObject verb) fs
+            ]
 
 instance
   ( Ledger.Era ledgerera
@@ -264,7 +264,7 @@ instance
   , ToObject (PredicateFailure (Core.EraRule "UTXOW" ledgerera))
   ) => ToObject (ShelleyLedgerPredFailure ledgerera) where
   toObject verb (UtxowFailure f) = toObject verb f
-  toObject _verb (DelegsFailure _f) = error "TODO: Conway era" --toObject verb f
+  toObject verb (DelegsFailure f) = toObject verb f
 
 instance
   ( ToObject (PredicateFailure (Core.EraRule "CERTS" ledgerera))
@@ -284,23 +284,17 @@ instance ToObject (Conway.ConwayTallyPredFailure era) where
             , "govActionId" .= govActionIdToText govActionId
             ]
 
-  -- TODO: Implement
-instance ToObject (Conway.ConwayCertsPredFailure era) where
-  toObject _ _ = mempty
-
--- instance
---   ( ToObject (PredicateFailure (Ledger.EraRule "CERT" ledgerera))
---   ) => ToObject (Conway.ConwayDelegsPredFailure ledgerera) where
---   toObject _ (Conway.DelegateeNotRegisteredDELEG poolID) =
---     mconcat [ "kind" .= String "DelegateeNotRegisteredDELEG"
---              , "poolID" .= String (textShow poolID)
---             ]
---   toObject _ (Conway.WithdrawalsNotInRewardsDELEGS rs) =
---     mconcat [ "kind" .= String "WithdrawalsNotInRewardsDELEGS"
---              , "rewardAccounts" .= rs
---             ]
---   toObject v (Conway.CertFailure certFailure) =
---     toObject v certFailure
+instance
+  ( Core.Crypto (Consensus.EraCrypto era)
+  , ToObject (PredicateFailure (Ledger.EraRule "CERT" era))
+  ) => ToObject (Conway.ConwayCertsPredFailure era) where
+  toObject verb = \case
+    Conway.DelegateeNotRegisteredDELEG targetPool ->
+      mconcat [ "kind" .= String "DelegateeNotRegisteredDELEG" , "targetPool" .= targetPool ]
+    Conway.WithdrawalsNotInRewardsCERTS incorrectWithdrawals ->
+      mconcat [ "kind" .= String "WithdrawalsNotInRewardsCERTS" , "incorrectWithdrawals" .= incorrectWithdrawals ]
+    Conway.CertFailure f -> toObject verb f
+
 
 instance
   ( ToObject (PPUPPredFailure ledgerera)
```
