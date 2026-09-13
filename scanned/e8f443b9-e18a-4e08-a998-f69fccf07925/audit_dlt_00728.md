# [?] hardening: Add range checks to prevent signed integer overflow UB.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-10
Source: https://github.com/zcash/zcash/commit/de16cd0a0c7cc7f9be8ce164d17ca970b20c0feb
Type: security-commit

## Details
hardening: Add range checks to prevent signed integer overflow UB.

Add range checks for integer arithmetic on CAmount values to prevent
signed integer overflow (undefined behavior in C++).

In SetChainPoolValues: check each running sum of per-pool deltas
(saplingValue, orchardValue, sproutValue) after every mutation,
ensuring it stays within [-MAX_MONEY, MAX_MONEY]. Make the function
return bool so callers can reject blocks with out-of-range deltas.

In ReceivedBlockTransactions: check parent chain values are in
MoneyRange and per-block deltas are in MoneyDeltaRange before each
addition.

In ConnectBlock: check chainSupplyDelta, transparentValueDelta,
cbTotalOutputValue, cbTotalInputValue, txFee, and nFees after each
mutation. Check parent nChainTotalSupply and nChainTransparentValue
are in MoneyRange before and after accumulating.

In LoadBlockIndexDB: add the same pre- and post-addition checks for
all six pool value accumulations and the total supply / transparent
value accumulations. On-disk per-block deltas could be corrupted by
a prior vulnerable version, so we cannot assume they are in range.

In GetTransparentValueIn and GetValueIn: add MoneyRange checks on
the running sum, matching the existing checks in GetValueOut and
GetShieldedValueIn. GetTransparentValueIn can sum up to ~48K inputs
per block (MAX_BLOCK_SIZE / ~41 bytes per input), which at MAX_MONEY
each would exceed INT64_MAX. The intermediate overflow cannot be
prevented at call sites, only inside the loop. Throwing is consistent
with GetValueOut and GetShieldedValueIn, which already throw on range
violations, so callers already need to handle exceptions from value
computation.

Add a MoneyDeltaRange helper ([-MAX_MONEY, MAX_MONEY]) alongside the
existing MoneyRange ([0, MAX_MONEY]) for checking per-block deltas
that may be negative. Use it in GetValueOut for consistency.

Use .value() instead of * for optional dereferences in code touched
by this commit.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### src/amount.h
```diff
@@ -31,6 +31,7 @@ extern const std::string MINOR_CURRENCY_UNIT;
  * */
 static const CAmount MAX_MONEY = 21000000 * COIN;
 inline bool MoneyRange(const CAmount& nValue) { return (nValue >= 0 && nValue <= MAX_MONEY); }
+inline bool MoneyDeltaRange(const CAmount& nValue) { return (nValue >= -MAX_MONEY && nValue <= MAX_MONEY); }
 
 /** The legacy default fee that was defined in ZIP 313. */
 static const CAmount LEGACY_DEFAULT_FEE = 1000;
```

### src/coins.cpp
```diff
@@ -1036,7 +1036,11 @@ const CTxOut &CCoinsViewCache::GetOutputFor(const CTxIn& input) const
 
 CAmount CCoinsViewCache::GetValueIn(const CTransaction& tx) const
 {
-    return GetTransparentValueIn(tx) + tx.GetShieldedValueIn();
+    CAmount nResult = GetTransparentValueIn(tx) + tx.GetShieldedValueIn();
+    if (!MoneyRange(nResult)) {
+        throw std::runtime_error("CCoinsViewCache::GetValueIn(): nResult out of range");
+    }
+    return nResult;
 }
 
 CAmount CCoinsViewCache::GetTransparentValueIn(const CTransaction& tx) const
@@ -1045,8 +1049,12 @@ CAmount CCoinsViewCache::GetTransparentValueIn(const CTransaction& tx) const
         return 0;
 
     CAmount nResult = 0;
-    for (unsigned int i = 0; i < tx.vin.size(); i++)
+    for (unsigned int i = 0; i < tx.vin.size(); i++) {
         nResult += GetOutputFor(tx.vin[i]).nValue;
+        if (!MoneyRange(nResult)) {
+            throw std::runtime_error("CCoinsViewCache::GetTransparentValueIn(): nResult out of range");
+        }
+    }
 
     return nResult;
 }
```

### src/gtest/test_validation.cpp
```diff
@@ -10,7 +10,7 @@
 
 #include <optional>
 
-extern void SetChainPoolValues(
+extern bool SetChainPoolValues(
     const CChainParams& chainparams,
     const CBlock &block,
     CBlockIndex *pindex);
```

### src/main.cpp
```diff
@@ -3278,6 +3278,9 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
     // Initialize the chain supply delta to the value delta of the lockbox for the block,
     // as previously computed using `SetChainPoolValues`.
     CAmount chainSupplyDelta = pindex->nLockboxValue;
+    if (!MoneyDeltaRange(chainSupplyDelta)) {
+        return error("%s: chain supply delta out of range: %d at height %d", __func__, chainSupplyDelta, pindex->nHeight);
+    }
     CAmount transparentValueDelta = 0;
     size_t total_sapling_tx = 0;
     size_t total_orchard_tx = 0;
@@ -3316,6 +3319,9 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
             for (const auto& input : tx.vin) {
                 const auto prevout = view.GetOutputFor(input);
                 transparentValueDelta -= prevout.nValue;
+                if (!MoneyDeltaRange(transparentValueDelta)) {
+                    return error("%s: transparent value delta out of range: %d at height %d", __func__, transparentValueDelta, pindex->nHeight);
+                }
                 allPrevOutputs.push_back(prevout);
             }
 
@@ -3382,14 +3388,26 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
             // - This includes fees, which are then canceled out by the fee subtractions
             //   in the other branch of this conditional.
             chainSupplyDelta += tx.GetValueOut();
+            if (!MoneyDeltaRange(chainSupplyDelta)) {
+                return error("%s: chain supply delta out of range: %d at height %d", __func__, chainSupplyDelta, pindex->nHeight);
+            }
         } else {
             const auto txFee = view.GetValueIn(tx) - tx.GetValueOut();
+            if (!MoneyRange(txFee)) {
+                return error("%s: transaction fee out of range: %d at height %d", __func__, txFee, pindex->nHeight);
+            }
             nFees += txFee;
+            if (!MoneyRange(nFees)) {
+                return error("%s: total fees out of range: %d at height %d", __func__, nFees, pindex->nHeight);
+            }
 
             // Fees from a transaction do not go into an output of the transaction,
             // and therefore decrease the chain supply. If the miner claims them,
             // they will be re-added in the other branch of this conditional.
             chainSupplyDelta -= txFee;
+            if (!MoneyDeltaRange(chainSupplyDelta)) {
+                return error("%s: chain supply delta out of range: %d at height %d", __func__, chainSupplyDelta, pindex->nHeight);
+            }
 
             std::vector<CScriptCheck> vChecks;
             if (!ContextualCheckInputs(tx, state, view, fExpensiveChecks, flags, fCacheResults, txdata.back(), consensusParams, consensusBranchId, nScriptCheckThreads ? &vChecks : NULL))
@@ -3496,6 +3514,9 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
 
         for (const auto& out : tx.vout) {
             transparentValueDelta += out.nValue;
+            if (!MoneyDeltaRange(transparentValueDelta)) {
+                return error("%s: transparent value delta out of range: %d at height %d", __func__, transparentValueDelta, pindex->nHeight);
+            }
         }
 
         if (tx.GetSaplingBundle().IsPresent()) {
@@ -3531,13 +3552,29 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
         pindex->nTransparentValue = transparentValueDelta;
         if (pindex->pprev) {
             if (pindex->pprev->nChainTotalSupply) {
-                pindex->nChainTotalSupply = *pindex->pprev->nChainTotalSupply + chainSupplyDelta;
+                CAmount chainTotalSupply = pindex->pprev->nChainTotalSupply.value();
+                if (!MoneyRange(chainTotalSupply)) {
+                    return error("%s: previous total supply out of range: %d at height %d", __func__, chainTotalSupply, pindex->nHeight);
+                }
+                chainTotalSupply += chainSupplyDelta;
+                if (!MoneyRange(chainTotalSupply)) {
+                    return error("%s: new total supply out of range: %d at height %d", __func__, chainTotalSupply, pindex->nHeight);
+                }
+                pindex->nChainTotalSupply = chainTotalSupply;
             } else {
                 pindex->nChainTotalSupply = std::nullopt;
             }
 
             if (pindex->pprev->nChainTransparentValue) {
-                pindex->nChainTransparentValue = *pindex->pprev->nChainTransparentValue + transparentValueDelta;
+                CAmount chainTransparentValue = pindex->pprev->nChainTransparentValue.value();
+                if (!MoneyRange(chainTransparentValue)) {
+                    return error("%s: previous chain transparent value out of range: %d at height %d", __func__, chainTransparentValue, pindex->nHeight);
+                }
+                chainTransparentValue += transparentValueDelta;
+                if (!MoneyRange(chainTransparentValue)) {
+                    return error("%s: new chain transparent value out of range: %d at height %d", __func__, chainTransparentValue, pindex->nHeight);
+                }
+                pindex->nChainTransparentValue = chainTransparentValue;
             } else {
                 pindex->nChainTransparentValue = std::nullopt;
             }
@@ -3655,7 +3692,15 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
     LogPrint("bench", "      - Connect %u transactions: %.2fms (%.3fms/tx, %.3fms/txin) [%.2fs]\n", (unsigned)block.vtx.size(), 0.001 * (nTime1 - nTimeStart), 0.001 * (nTime1 - nTimeStart) / block.vtx.size(), nInputs <= 1 ? 0 : 0.001 * (nTime1 - nTimeStart) / (nInputs-1), nTimeConnect * 0.000001);
 
     CAmount cbTotalOutputValue = block.vtx[0].GetValueOut() + pindex->nLockboxValue;
+    if (!MoneyRange(cbTotalOutputValue)) {
+        return state.DoS(100, error("%s: coinbase output value out of range at height %d", __func__, pindex->nHeight),
+            REJECT_INVALID, "bad-cb-output-value-out-of-range");
+    }
     CAmount cbTotalInputValue = consensusParams.GetBlockSubsidy(pindex->nHeight) + nFees;
+    if (!MoneyRange(cbTotalInputValue)) {
+        return state.DoS(100, error("%s: coinbase input value out of range at height %d", __func__, pindex->nHeight),
+            REJECT_INVALID, "bad-cb-input-value-out-of-range");
+    }
     if (cbTotalOutputValue > cbTotalInputValue) {
         return state.DoS(100,
             error("%s: coinbase pays too much (actual=%d vs limit=%d)", __func__,
@@ -3683,6 +3728,15 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
             pindex->nChainOrchardValue.has_value() &&
             pindex->nChainLockboxValue.has_value())
     {
+        if (!MoneyRange(pindex->nChainTotalSupply.value()) ||
+            !MoneyRange(pindex->nChainTransparentValue.value()) ||
+            !MoneyRange(pindex->nChainSproutValue.value()) ||
+            !MoneyRange(pindex->nChainSaplingValue.value()) ||
+            !MoneyRange(pindex->nChainOrchardValue.value()) ||
+            !MoneyRange(pindex->nChainLockboxValue.value())) {
+            return state.DoS(100, error("%s: chain accounting value out of range at height %d", __func__, pindex->nHeight),
+                REJECT_INVALID, "bad-chain-supply-out-of-range");
+        }
         auto expectedChainSupply =
             pindex->nChainTransparentValue.value() +
             pindex->nChainSproutValue.value() +
@@ -4713,7 +4767,10 @@ void FallbackSproutValuePoolBalance(
 
 // Compute the effect of `block` on the chain supply and the value in each value pool.
 // This requires `pindex->nHeight` and `pindex->pprev` to be set, but nothing else.
-void SetChainPoolValues(
+//
+// Returns false if the block's aggregate per-pool value deltas overflow the
+// valid monetary range at any step of the accumulation.
+bool SetChainPoolValues(
     const CChainParams& chainparams,
     const CBlock &block,
     CBlockIndex *pindex)
@@ -4753,14 +4810,26 @@ void SetChainPoolValues(
         // and adds it to the Sapling value pool. Positive valueBalanceSapling "gives"
         // money to the transparent value pool, removing from the Sapling value
         // pool. So we invert the sign here.
-        saplingValue += -tx.GetValueBalanceSapling();
+        saplingValue -= tx.GetValueBalanceSapling();
+        if (!MoneyDeltaRange(saplingValue)) {
+            return error("%s: sapling value delta out of range: %d at height %d", __func__, saplingValue, pindex->nHeight);
+        }
 
         // valueBalanceOrchard behaves the same way as valueBalanceSapling.
-        orchardValue += -tx.GetOrchardBundle().GetValueBalance();
+        orchardValue -= tx.GetOrchardBundle().GetValueBalance();
+        if (!MoneyDeltaRange(orchardValue)) {
+            return error("%s: orchard value delta out of range: %d at height %d", __func__, orchardValue, pindex->nHeight);
+        }
 
         for (auto js : tx.vJoinSplit) {
             sproutValue += js.vpub_old;
+            if (!MoneyDeltaRange(sproutValue)) {
+                return error("%s: sprout value delta out of range: %d at height %d", __func__, sproutValue, pindex->nHeight);
+            }
             sproutValue -= js.vpub_new;
+            if (!MoneyDeltaRange(sproutValue)) {
+                return error("%s: sprout value delta out of range: %d at height %d", __func__, sproutValue, pindex->nHeight);
+            }
         }
     }
 
@@ -4785,6 +4854,8 @@ void SetChainPoolValues(
     pindex->nChainOrchardValue = std::nullopt;
     pindex->nLockboxValue = lockboxValue;
     pindex->nChainLockboxValue = std::nullopt;
+
+    return true;
 }
 
 /**
@@ -4798,7 +4869,9 @@ bool ReceivedBlockTransactions(
     CBlockIndex *pindexNew,
     const CDiskBlockPos& pos)
 {
-    SetChainPoolValues(chainparams, block, pindexNew);
+    if (!SetChainPoolValues(chainparams, block, pindexNew)) {
+        return error("ReceivedBlockTransactions(): SetChainPoolValues failed");
+    }
 
     pindexNew->nTx = block.vtx.size();
     pindexNew->nChainTx = 0;
@@ -4826,30 +4899,46 @@ bool ReceivedBlockTransactions(
                 // place that we have a valid coins view with which to compute
                 // the transparent input value and fees.
 
-                // Calculate the block's effect on the Sprout chain value pool balance.
-                if (pindex->pprev->nChainSproutValue && pindex->nSproutValue) {
-                    pindex->nChainSproutValue = *pindex->pprev->nChainSproutValue + *pindex->nSproutValue;
+                // Calculate the block's effect on the Sapling chain value pool balance.
+                if (pindex->pprev->nChainSproutValue.has_value() && pindex->nSproutValue.has_value()) {
+                    CAmount chainSproutValue = pindex->pprev->nChainSproutValue.value();
+                    if (!MoneyRange(chainSproutValue) || !MoneyDeltaRange(pindex->nSproutValue.value())) {
+                        return error("%s: previous sprout pool value out of range at height %d", __func__, pindex->nHeight);
+                    }
+                    pindex->nChainSproutValue = chainSproutValue + pindex->nSproutValue.value();
                 } else {
                     pindex->nChainSproutValue = std::nullopt;
                 }
 
                 // Calculate the block's effect on the Sapling chain value pool balance.
-                if (pindex->pprev->nChainSaplingValue) {
-                    pindex->nChainSaplingValue = *pindex->pprev->nChainSaplingValue + pindex->nSaplingValue;
+                if (pindex->pprev->nChainSaplingValue.has_value()) {
+                    CAmount chainSaplingValue = pindex->pprev->nChainSaplingValue.value();
+                    if (!MoneyRange(chainSaplingValue) || !MoneyDeltaRange(pindex->nSaplingValue)) {
+                        return error("%s: previous sapling pool value out of range at height %d", __func__, pindex->nHeight);
+                    }
+                    pindex->nChainSaplingValue = chainSaplingValue + pindex->nSaplingValue;
                 } else {
                     pindex->nChainSaplingValue = std::nullopt;
                 }
 
                 // Calculate the block's effect on the Orchard chain value pool balance.
-                if (pindex->pprev->nChainOrchardValue) {
-                    pindex->nChainOrchardValue = *pindex->pprev->nChainOrchardValue + pindex->nOrchardValue;
+                if (pindex->pprev->nChainOrchardValue.has_value()) {
+                    CAmount chainOrchardValue = pindex->pprev->nChainOrchardValue.value();
+                    if (!MoneyRange(chainOrchardValue) || !MoneyDeltaRange(pindex->nOrchardValue)) {
+                        return error("%s: previous orchard pool value out of range at height %d", __func__, pindex->nHeight);
+                    }
+                    pindex->nChainOrchardValue = chainOrchardValue + pindex->nOrchardValue;
                 } else {
                     pindex->nChainOrchardValue = std::nullopt;
                 }
 
                 // Calculate the block's effect on the Lockbox balance
-                if (pindex->pprev->nChainLockboxValue) {
-                    pindex->nChainLockboxValue = *pindex->pprev->nChainLockboxValue + pindex->nLockboxValue;
+                if (pindex->pprev->nChainLockboxValue.has_value()) {
+                    CAmount chainLockboxValue = pindex->pprev->nChainLockboxValue.value();
+                    if (!MoneyRange(chainLockboxValue) || !MoneyDeltaRange(pindex->nLockboxValue)) {
+                        return error("%s: previous lockbox pool value out of range at height %d", __func__, pindex->nHeight);
+                    }
+                    pindex->nChainLockboxValue = chainLockboxValue + pindex->nLockboxValue;
                 } else {
                     pindex->nChainLockboxValue = std::nullopt;
                 }
@@ -5418,7 +5507,9 @@ bool TestBlockValidity(
     CBlockIndex indexDummy(block);
     indexDummy.pprev = pindexPrev;
     indexDummy.nHeight = pindexPrev->nHeight + 1;
-    SetChainPoolValues(chainparams, block, &indexDummy);
+    if (!SetChainPoolValues(chainparams, block, &indexDummy)) {
+        return false;
+    }
 
     // JoinSplit proofs are verified in ConnectBlock
     auto verifier = ProofVerifier::Disabled();
@@ -5638,38 +5729,90 @@ bool static LoadBlockIndexDB(const CChainParams& chainparams)
                 if (pindex->pprev->nChainTx) {
                     pindex->nChainTx = pindex->pprev->nChainTx + pindex->nTx;
 
-                    if (pindex->pprev->nChainTotalSupply && pindex->nChainSupplyDelta) {
-                        pindex->nChainTotalSupply = *pindex->pprev->nChainTotalSupply + *pindex->nChainSupplyDelta;
+                    // Pre-addition range checks to prevent signed integer
+                    // overflow (UB). On-disk per-block deltas could be
+                    // corrupted, so we cannot assume they are in range.
+
+                    if (pindex->pprev->nChainTotalSupply.has_value() && pindex->nChainSupplyDelta.has_value()) {
+                        CAmount chainTotalSupply = pindex->pprev->nChainTotalSupply.value();
+                        if (!MoneyRange(chainTotalSupply) || !MoneyDeltaRange(pindex->nChainSupplyDelta.value())) {
+                            return error("%s: previous total supply value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainTotalSupply += pindex->nChainSupplyDelta.value();
+                        if (!MoneyRange(chainTotalSupply)) {
+                            return error("%s: new total supply value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainTotalSupply = chainTotalSupply;
                     } else {
                         pindex->nChainTotalSupply = std::nullopt;
                     }
 
-                    if (pindex->pprev->nChainTransparentValue && pindex->nTransparentValue) {
-                        pindex->nChainTransparentValue = *pindex->pprev->nChainTransparentValue + *pindex->nTransparentValue;
+                    if (pindex->pprev->nChainTransparentValue.has_value() && pindex->nTransparentValue.has_value()) {
+                        CAmount chainTransparentValue = pindex->pprev->nChainTransparentValue.value();
+                        if (!MoneyRange(chainTransparentValue) || !MoneyDeltaRange(pindex->nTransparentValue.value())) {
+                            return error("%s: previous transparent value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainTransparentValue += pindex->nTransparentValue.value();
+                        if (!MoneyRange(chainTransparentValue)) {
+                            return error("%s: new transparent value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainTransparentValue = chainTransparentValue;
                     } else {
                         pindex->nChainTransparentValue = std::nullopt;
                     }
 
-                    if (pindex->pprev->nChainSproutValue && pindex->nSproutValue) {
-                        pindex->nChainSproutValue = *pindex->pprev->nChainSproutValue + *pindex->nSproutValue;
+                    if (pindex->pprev->nChainSproutValue.has_value() && pindex->nSproutValue.has_value()) {
+                        CAmount chainSproutValue = pindex->pprev->nChainSproutValue.value();
+                        if (!MoneyRange(chainSproutValue) || !MoneyDeltaRange(pindex->nSproutValue.value())) {
+                            return error("%s: previous sprout value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainSproutValue += pindex->nSproutValue.value();
+                        if (!MoneyRange(chainSproutValue)) {
+                            return error("%s: new sprout value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainSproutValue = chainSproutValue;
                     } else {
                         pindex->nChainSproutValue = std::nullopt;
                     }
 
-                    if (pindex->pprev->nChainSaplingValue) {
-                        pindex->nChainSaplingValue = *pindex->pprev->nChainSaplingValue + pindex->nSaplingValue;
+                    if (pindex->pprev->nChainSaplingValue.has_value()) {
+                        CAmount chainSaplingValue = pindex->pprev->nChainSaplingValue.value();
+                        if (!MoneyRange(chainSaplingValue) || !MoneyDeltaRange(pindex->nSaplingValue)) {
+                            return error("%s: previous sapling value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainSaplingValue += pindex->nSaplingValue;
+                        if (!MoneyRange(chainSaplingValue)) {
+                            return error("%s: new sapling value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainSaplingValue = chainSaplingValue;
                     } else {
                         pindex->nChainSaplingValue = std::nullopt;
                     }
 
-                    if (pindex->pprev->nChainOrchardValue) {
-                        pindex->nChainOrchardValue = *pindex->pprev->nChainOrchardValue + pindex->nOrchardValue;
+                    if (pindex->pprev->nChainOrchardValue.has_value()) {
+                        CAmount chainOrchardValue = pindex->pprev->nChainOrchardValue.value();
+                        if (!MoneyRange(chainOrchardValue) || !MoneyDeltaRange(pindex->nOrchardValue)) {
+                            return error("%s: previous orchard value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainOrchardValue += pindex->nOrchardValue;
+                        if (!MoneyRange(chainOrchardValue)) {
+                            return error("%s: new orchard value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainOrchardValue = chainOrchardValue;
                     } else {
                         pindex->nChainOrchardValue = std::nullopt;
                     }
 
-                    if (pindex->pprev->nChainLockboxValue) {
-                        pindex->nChainLockboxValue = *pindex->pprev->nChainLockboxValue + pindex->nLockboxValue;
+                    if (pindex->pprev->nChainLockboxValue.has_value()) {
+                        CAmount chainLockboxValue = pindex->pprev->nChainLockboxValue.value();
+                        if (!MoneyRange(chainLockboxValue) || !MoneyDeltaRange(pindex->nLockboxValue)) {
+                            return error("%s: previous lockbox value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        chainLockboxValue += pindex->nLockboxValue;
+                        if (!MoneyRange(chainLockboxValue)) {
+                            return error("%s: new lockbox value out of range at height %d", __func__, pindex->nHeight);
+                        }
+                        pindex->nChainLockboxValue = chainLockboxValue;
                     } else {
                         pindex->nChainLockboxValue = std::nullopt;
                     }
```

### src/primitives/transaction.cpp
```diff
@@ -227,7 +227,7 @@ CAmount CTransaction::GetValueOut() const
     auto valueBalanceSapling = saplingBundle.GetValueBalance();
     if (valueBalanceSapling <= 0) {
         // NB: negative valueBalanceSapling "takes" money from the transparent value pool just as outputs do
-        if (valueBalanceSapling < -MAX_MONEY) {
+        if (!MoneyDeltaRange(valueBalanceSapling)) {
             throw std::runtime_error("CTransaction::GetValueOut(): valueBalanceSapling out of range");
         }
         nValueOut += -valueBalanceSapling;
@@ -240,7 +240,7 @@ CAmount CTransaction::GetValueOut() const
     auto valueBalanceOrchard = orchardBundle.GetValueBalance();
     if (valueBalanceOrchard <= 0) {
         // NB: negative valueBalanceOrchard "takes" money from the transparent value pool just as outputs do
-        if (valueBalanceOrchard < -MAX_MONEY) {
+        if (!MoneyDeltaRange(valueBalanceOrchard)) {
             throw std::runtime_error("CTransaction::GetValueOut(): valueBalanceOrchard out of range");
         }
         nValueOut += -valueBalanceOrchard;
```
