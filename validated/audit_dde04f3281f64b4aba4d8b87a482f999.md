Based on my thorough investigation of the codebase, I need to assess whether there is a valid analog to the ETH lockup bug in the sequencer.

The external bug's invariant: **when a resource is partially consumed in a callback/swap, the unconsumed remainder is permanently locked rather than returned.**

Let me do one final targeted search to check the `handle_executed_txs` path and the `l2_gas_used` accounting when `final_n_executed_txs < n_executed_txs`.