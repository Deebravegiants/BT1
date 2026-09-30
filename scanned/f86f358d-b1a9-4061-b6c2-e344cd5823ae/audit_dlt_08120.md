# [?] Blockchain: fix data race in get_dynamic_base_fee_estimate

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2026-06-12
Source: https://github.com/monero-project/monero/commit/95b207f00f67e2945e89e22038faaf7561c1b88f
Type: security-commit

## Details
Blockchain: fix data race in get_dynamic_base_fee_estimate

## Patch
### src/cryptonote_core/blockchain.cpp
```diff
@@ -3654,6 +3654,7 @@ void Blockchain::get_dynamic_base_fee_estimate_2021_scaling(uint64_t base_reward
 
 void Blockchain::get_dynamic_base_fee_estimate_2021_scaling(uint64_t grace_blocks, std::vector<uint64_t> &fees) const
 {
+  CRITICAL_REGION_LOCAL(m_blockchain_lock);
   const uint8_t version = get_current_hard_fork_version();
   const uint64_t db_height = m_db->height();
 
```
