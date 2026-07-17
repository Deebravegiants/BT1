Let me examine the relevant code to evaluate this claim.

Let me look at the key divergence point: `record_contract_call` uses `state_update.trie.get_optimized_ref(...)` directly, while `TrieUpdate::get_ref` checks the overlay first.