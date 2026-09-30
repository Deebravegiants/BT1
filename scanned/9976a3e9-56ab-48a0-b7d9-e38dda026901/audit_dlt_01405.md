# [?] Merge bitcoin/bitcoin#34908: rpc, refactor: gettxoutsetinfo race condition fix follow-ups

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-04-20
Source: https://github.com/bitcoin/bitcoin/commit/b6d1b65062ab123248e4f209fe3f63118f03bad6
Type: security-commit

## Details
Merge bitcoin/bitcoin#34908: rpc, refactor: gettxoutsetinfo race condition fix follow-ups

3e5dc610353ef16b0e7f391faaac77da6f4a0fab rpc, refactor: gettxoutsetinfo race condition fix follow-ups (rkrux)

Pull request description:

  This patch addresses my own review comments from the review of #34451. If these are found helpful, it makes sense to do them now after the previous PR was merged and backported.

  Pasting the comments below that also explains the changes:

  - Move the pindex declaration below now that it is not used earlier.
  - stats was being generated partially in both these ComputeUTXOStats functions, which reads oddly to me. Now that the pcursor is also moved and passed to this function, which reads oddly as well, I believe we can refactor this function to completely build the stats inside this function. A side benefit is that by removing the stats and pcursor arguments, the function signature becomes quite similar to its namesake, which in turn becomes a straightforward wrapper of this function.

ACKs for top commit:
  w0xlt:
    ACK 3e5dc610353ef16b0e7f391faaac77da6f4a0fab
  sedited:
    ACK 3e5dc610353ef16b0e7f391faaac77da6f4a0fab

Tree-SHA512: b8e4a4ebfe4935aa97920cb7068445ea93e571f80e679b8791343ac8750b48484d4288e083e07bf433b397cb6071171a2b77d34758a4627056b34cc63d06f0f4

## Patch
### src/kernel/coinstats.cpp
```diff
@@ -108,9 +108,17 @@ static void ApplyStats(CCoinsStats& stats, const std::map<uint32_t, Coin>& outpu
 
 //! Calculate statistics about the unspent transaction output set
 template <typename T>
-static bool ComputeUTXOStats(CCoinsView* view, CCoinsStats& stats, T hash_obj, const std::function<void()>& interruption_point, std::unique_ptr<CCoinsViewCursor> pcursor)
+static std::optional<CCoinsStats> ComputeUTXOStats(T hash_obj, CCoinsView* view, node::BlockManager& blockman, const std::function<void()>& interruption_point)
 {
+    std::unique_ptr<CCoinsViewCursor> pcursor;
+    CBlockIndex* pindex;
+    {
+        LOCK(::cs_main);
+        pcursor = view->Cursor();
+        pindex = blockman.LookupBlockIndex(pcursor->GetBestBlock());
+    }
     assert(pcursor);
+    CCoinsStats stats{Assert(pindex)->nHeight, pindex->GetBlockHash()};
 
     Txid prevkey;
     std::map<uint32_t, Coin> outputs;
@@ -129,7 +137,7 @@ static bool ComputeUTXOStats(CCoinsView* view, CCoinsStats& stats, T hash_obj, c
             stats.coins_count++;
         } else {
             LogError("%s: unable to read value\n", __func__);
-            return false;
+            return std::nullopt;
         }
         pcursor->Next();
     }
@@ -141,42 +149,27 @@ static bool ComputeUTXOStats(CCoinsView* view, CCoinsStats& stats, T hash_obj, c
     FinalizeHash(hash_obj, stats);
 
     stats.nDiskSize = view->EstimateSize();
-
-    return true;
+    return stats;
 }
 
 std::optional<CCoinsStats> ComputeUTXOStats(CoinStatsHashType hash_type, CCoinsView* view, node::BlockManager& blockman, const std::function<void()>& interruption_point)
 {
-    std::unique_ptr<CCoinsViewCursor> pcursor;
-    CBlockIndex* pindex;
-    {
-        LOCK(::cs_main);
-        pcursor = view->Cursor();
-        pindex = blockman.LookupBlockIndex(pcursor->GetBestBlock());
-    }
-    CCoinsStats stats{Assert(pindex)->nHeight, pindex->GetBlockHash()};
-
-    bool success = [&]() -> bool {
+    return [&]() -> std::optional<CCoinsStats> {
         switch (hash_type) {
         case(CoinStatsHashType::HASH_SERIALIZED): {
             HashWriter ss{};
-            return ComputeUTXOStats(view, stats, ss, interruption_point, std::move(pcursor));
+            return ComputeUTXOStats(ss, view, blockman, interruption_point);
         }
         case(CoinStatsHashType::MUHASH): {
             MuHash3072 muhash;
-            return ComputeUTXOStats(view, stats, muhash, interruption_point, std::move(pcursor));
+            return ComputeUTXOStats(muhash, view, blockman, interruption_point);
         }
         case(CoinStatsHashType::NONE): {
-            return ComputeUTXOStats(view, stats, nullptr, interruption_point, std::move(pcursor));
+            return ComputeUTXOStats(nullptr, view, blockman, interruption_point);
         }
         } // no default case, so the compiler can warn about missing cases
         assert(false);
     }();
-
-    if (!success) {
-        return std::nullopt;
-    }
-    return stats;
 }
 
 static void FinalizeHash(HashWriter& ss, CCoinsStats& stats)
```

### src/rpc/blockchain.cpp
```diff
@@ -1078,7 +1078,6 @@ static RPCMethod gettxoutsetinfo()
 {
     UniValue ret(UniValue::VOBJ);
 
-    const CBlockIndex* pindex{nullptr};
     const CoinStatsHashType hash_type{ParseHashType(self.Arg<std::string_view>("hash_type"))};
     bool index_requested = request.params[2].isNull() || request.params[2].get_bool();
 
@@ -1095,6 +1094,7 @@ static RPCMethod gettxoutsetinfo()
         blockman = &active_chainstate.m_blockman;
     }
 
+    const CBlockIndex* pindex{nullptr};
     if (!request.params[1].isNull()) {
         if (!g_coin_stats_index) {
             throw JSONRPCError(RPC_INVALID_PARAMETER, "Querying specific block heights requires coinstatsindex");
```
