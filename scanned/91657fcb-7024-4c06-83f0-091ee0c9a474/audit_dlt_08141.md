# [?] blockchain: Fix alt chain generated coins overflow

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-08-19
Source: https://github.com/monero-project/monero/commit/07cb087e5dd932c7afb9a7b2eafb99a003929e1f
Type: security-commit

## Details
blockchain: Fix alt chain generated coins overflow

Apply the overflow logic used for computing already_generated_coins in
the main chain to alternative chains.

## Patch
### src/cryptonote_core/blockchain.cpp
```diff
@@ -1739,7 +1739,8 @@ bool Blockchain::handle_alternative_block(const block& b, const crypto::hash& id
     const uint64_t prev_height = alt_chain.size() ? prev_data.height : m_db->get_block_height(b.prev_id);
     bei.height = prev_height + 1;
     uint64_t block_reward = get_outs_money_amount(b.miner_tx);
-    bei.already_generated_coins = block_reward + (alt_chain.size() ? prev_data.already_generated_coins : m_db->get_block_already_generated_coins(prev_height));
+    const uint64_t prev_generated_coins = alt_chain.size() ? prev_data.already_generated_coins : m_db->get_block_already_generated_coins(prev_height);
+    bei.already_generated_coins = (block_reward < (MONEY_SUPPLY - prev_generated_coins)) ? prev_generated_coins + block_reward : MONEY_SUPPLY;
 
     // verify that the block's timestamp is within the acceptable range
     // (not earlier than the median of the last X blocks)
```
