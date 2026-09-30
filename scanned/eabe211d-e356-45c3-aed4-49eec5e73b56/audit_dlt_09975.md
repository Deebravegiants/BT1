# [?] Fixing crash found by Anton

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2022-04-03
Source: https://github.com/litecoin-project/litecoin/commit/b05226fe1b5dbbc3f2588ab174115deeb0e08e1e
Type: security-commit

## Details
Fixing crash found by Anton

## Patch
### src/rpc/blockchain.cpp
```diff
@@ -513,15 +513,18 @@ static RPCHelpMan getdifficulty()
 static std::vector<RPCResult> MempoolEntryDescription() { return {
     RPCResult{RPCResult::Type::NUM, "vsize", "virtual transaction size as defined in BIP 141. This is different from actual serialized size for witness transactions as witness data is discounted."},
     RPCResult{RPCResult::Type::NUM, "weight", "transaction weight as defined in BIP 141."},
+    RPCResult{RPCResult::Type::NUM, "mwebweight", "transaction MWEB weight"},
     RPCResult{RPCResult::Type::STR_AMOUNT, "fee", "transaction fee in " + CURRENCY_UNIT + " (DEPRECATED)"},
     RPCResult{RPCResult::Type::STR_AMOUNT, "modifiedfee", "transaction fee with fee deltas used for mining priority (DEPRECATED)"},
     RPCResult{RPCResult::Type::NUM_TIME, "time", "local time transaction entered pool in seconds since 1 Jan 1970 GMT"},
     RPCResult{RPCResult::Type::NUM, "height", "block height when transaction entered pool"},
     RPCResult{RPCResult::Type::NUM, "descendantcount", "number of in-mempool descendant transactions (including this one)"},
     RPCResult{RPCResult::Type::NUM, "descendantsize", "virtual transaction size of in-mempool descendants (including this one)"},
+    RPCResult{RPCResult::Type::NUM, "descendantmwebweight", "transaction MWEB weight of in-mempool descendants (including this one)"},
     RPCResult{RPCResult::Type::STR_AMOUNT, "descendantfees", "modified fees (see above) of in-mempool descendants (including this one) (DEPRECATED)"},
     RPCResult{RPCResult::Type::NUM, "ancestorcount", "number of in-mempool ancestor transactions (including this one)"},
     RPCResult{RPCResult::Type::NUM, "ancestorsize", "virtual transaction size of in-mempool ancestors (including this one)"},
+    RPCResult{RPCResult::Type::NUM, "ancestormwebweight", "transaction MWEB weight of in-mempool ancestors (including this one)"},
     RPCResult{RPCResult::Type::STR_AMOUNT, "ancestorfees", "modified fees (see above) of in-mempool ancestors (including this one) (DEPRECATED)"},
     RPCResult{RPCResult::Type::STR_HEX, "wtxid", "hash of serialized transaction, including witness data"},
     RPCResult{RPCResult::Type::OBJ, "fees", "",
@@ -552,15 +555,18 @@ static void entryToJSON(const CTxMemPool& pool, UniValue& info, const CTxMemPool
 
     info.pushKV("vsize", (int)e.GetTxSize());
     info.pushKV("weight", (int)e.GetTxWeight());
+    info.pushKV("mwebweight", (int)e.GetMWEBWeight());
     info.pushKV("fee", ValueFromAmount(e.GetFee()));
     info.pushKV("modifiedfee", ValueFromAmount(e.GetModifiedFee()));
     info.pushKV("time", count_seconds(e.GetTime()));
     info.pushKV("height", (int)e.GetHeight());
     info.pushKV("descendantcount", e.GetCountWithDescendants());
     info.pushKV("descendantsize", e.GetSizeWithDescendants());
+    info.pushKV("descendantmwebweight", e.GetMWEBWeightWithDescendants());
     info.pushKV("descendantfees", e.GetModFeesWithDescendants());
     info.pushKV("ancestorcount", e.GetCountWithAncestors());
     info.pushKV("ancestorsize", e.GetSizeWithAncestors());
+    info.pushKV("ancestormwebweight", e.GetMWEBWeightWithAncestors());
     info.pushKV("ancestorfees", e.GetModFeesWithAncestors());
     info.pushKV("wtxid", pool.vTxHashes[e.vTxHashesIdx].first.ToString());
     const CTransaction& tx = e.GetTx();
```

### src/wallet/txlist.cpp
```diff
@@ -113,7 +113,7 @@ void TxList::List_Credit(std::vector<WalletTxRecord>& tx_records, const CWalletT
             } else {
                 // Received by IP connection (deprecated features), or a multisignature or other non-simple transaction
                 sub.type = WalletTxRecord::Type::RecvFromOther;
-                sub.address = wtx.mapValue.at("from");
+                sub.address = wtx.mapValue.count("from") > 0 ? wtx.mapValue.at("from") : "";
             }
 
             if (wtx.IsCoinBase()) {
@@ -174,7 +174,7 @@ void TxList::List_Debit(std::vector<WalletTxRecord>& tx_records, const CWalletTx
         } else {
             // Sent to IP, or other non-address transaction like OP_EVAL
             tx_record.type = WalletTxRecord::Type::SendToOther;
-            tx_record.address = wtx.mapValue.at("to");
+            tx_record.address = wtx.mapValue.count("to") > 0 ? wtx.mapValue.at("to") : "";
         }
 
         /* Add fee to first output */
```
