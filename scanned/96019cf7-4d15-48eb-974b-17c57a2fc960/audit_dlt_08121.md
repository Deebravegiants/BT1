# [?] tx_pool: fix use-after-free in prune()

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2026-06-03
Source: https://github.com/monero-project/monero/commit/b5f7330e0bcd2cc2d9e04919c78a609b8351b508
Type: security-commit

## Details
tx_pool: fix use-after-free in prune()
- txid was a reference to an item which was later deleted in remove_tx_from_transient_lists(), and txid was used after that

## Patch
### src/cryptonote_core/tx_pool.cpp
```diff
@@ -419,7 +419,7 @@ namespace cryptonote
         break;
       try
       {
-        const crypto::hash &txid = it->get_right();
+        const crypto::hash txid = it->get_right();
         txpool_tx_meta_t meta;
         if (!m_blockchain.get_txpool_tx_meta(txid, meta))
         {
```
