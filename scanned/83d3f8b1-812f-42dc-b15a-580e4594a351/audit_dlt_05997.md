# [?] Fix crash bug with duplicate inputs within a transaction

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2018-09-17
Source: https://github.com/dogecoin/dogecoin/commit/52965fbaef4b8ff310e01273817fb027389d3f80
Type: security-commit

## Details
Fix crash bug with duplicate inputs within a transaction

Introduced by #9049

Github-Pull: #14247

Tree-SHA512: 54ccf896e4c816ba8532644affc984a091ed801d8387bb01a836953c9ec4a345359d98fb58dd5f929617afd42bce0cc40293fecf943a1584207c82dd78da0ea5

## Patch
### src/validation.cpp
```diff
@@ -2880,7 +2880,7 @@ bool CheckBlock(const CBlock& block, CValidationState& state, const Consensus::P
 
     // Check transactions
     for (const auto& tx : block.vtx)
-        if (!CheckTransaction(*tx, state, false))
+        if (!CheckTransaction(*tx, state, true))
             return state.Invalid(false, state.GetRejectCode(), state.GetRejectReason(),
                                  strprintf("Transaction check failed (tx hash %s) %s", tx->GetHash().ToString(), state.GetDebugMessage()));
 
```
