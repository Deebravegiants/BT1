# [?] Fix minting policy in tutorial in light of https://www.tweag.io/blog/2022-03-25-minswap-lp-vulnerability/. (#4980)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2022-11-29
Source: https://github.com/IntersectMBO/plutus/commit/7dafcadd4eb18bfb25bef92c4d918dbb8e45a00d
Type: security-commit

## Details
Fix minting policy in tutorial in light of https://www.tweag.io/blog/2022-03-25-minswap-lp-vulnerability/. (#4980)

Co-authored-by: David Eichmann <EichmannD@gmail.com>

Co-authored-by: David Eichmann <EichmannD@gmail.com>

## Patch
### doc/read-the-docs-site/tutorials/BasicPolicies.hs
```diff
@@ -14,6 +14,7 @@ import PlutusLedgerApi.V1.Contexts
 import PlutusLedgerApi.V1.Crypto
 import PlutusLedgerApi.V1.Scripts
 import PlutusLedgerApi.V1.Value
+import PlutusTx.AssocMap qualified as Map
 
 tname :: TokenName
 tname = error ()
@@ -31,7 +32,14 @@ oneAtATimePolicy _ ctx =
         minted = txInfoMint txinfo
     -- Here we're looking at some specific token name, which we
     -- will assume we've got from elsewhere for now.
-    in valueOf minted ownSymbol tname == 1
+    in currencyValueOf minted ownSymbol == singleton ownSymbol tname 1
+
+{-# INLINABLE currencyValueOf #-}
+-- | Get the quantities of just the given 'CurrencySymbol' in the 'Value'.
+currencyValueOf :: Value -> CurrencySymbol -> Value
+currencyValueOf (Value m) c = case Map.lookup c m of
+    Nothing -> mempty
+    Just t  -> Value (Map.singleton c t)
 -- BLOCK2
 -- The 'plutus-ledger' package from 'plutus-apps' provides helper functions to automate
 -- some of this boilerplate.
```

### doc/read-the-docs-site/tutorials/basic-minting-policies.rst
```diff
@@ -23,13 +23,15 @@ Plutus script context versions
 ------------------------------------
 
 Minting policies have access to the :term:`script context` as their second argument.
-Each version of Plutus minting policy scripts are differentiated only by their ``ScriptContext`` argument. 
+Each version of Plutus minting policy scripts are differentiated only by their ``ScriptContext`` argument.
 
-   See this example from the file ``MustSpendScriptOutput.hs`` (lines 340 to 422) showing code addressing `Versioned Policies for both Plutus V1 and Plutus V2 <https://github.com/input-output-hk/plutus-apps/blob/05e394fb6188abbbe827ff8a51a24541a6386422/plutus-contract/test/Spec/TxConstraints/MustSpendScriptOutput.hs#L340-L422>`_. 
+   See this example from the file ``MustSpendScriptOutput.hs`` (lines 340 to 422) showing code addressing `Versioned Policies for both Plutus V1 and Plutus V2 <https://github.com/input-output-hk/plutus-apps/blob/05e394fb6188abbbe827ff8a51a24541a6386422/plutus-contract/test/Spec/TxConstraints/MustSpendScriptOutput.hs#L340-L422>`_.
 
 Minting policies tend to be particularly interested in the ``mint`` field, since the point of a minting policy is to control which tokens are minted.
 
-It is also important for a minting policy to look at the tokens in the ``mint`` field that are part of its own asset group.
+It is also important for a minting policy to look at the tokens in the ``mint`` field that use its own currency symbol i.e. policy hash.
+Note that checking only a specific token name is usually not correct.
+The minting policy must check for correct minting (or lack there of) of all token names under its currency symbol.
 This requires the policy to refer to its own hash --- fortunately this is provided for us in the script context of a minting policy.
 
 Writing minting policies
```
