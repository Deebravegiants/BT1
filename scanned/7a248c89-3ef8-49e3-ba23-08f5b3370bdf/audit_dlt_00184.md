# [H] CometBFT may duplicate transactions in the mempool's data structures

## Summary
Severity: High
Chain: Cosmos
Component: github.com/cometbft/cometbft
CVE: CVE-2023-34451
CWE: Missing Release of Memory after Effective Lifetime
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-w24w-wp77-qffm
Type: github-advisory

## Details
### Impact

The mempool maintains two data structures to keep track of outstanding transactions: a list and a map.
These two data structures are supposed to be in sync all the time in the sense that the map tracks the index (if any) of the transaction in the list. 

Unfortunately, it is possible to have them out of sync. When this happens, the list may contain several copies of the same transaction.
Because the map tracks a single index, it is then no longer possible to remove all the copies of the transaction from the list.
This happens  even if the duplicated transaction is later committed in a block.
The only way to remove the transaction is by restarting the node.

These are the steps to cause the above duplication problem. Everything should happen within one height, that is no `FinalizeBlock` or `BeginBlock` ABCI calls should happen while these steps are reproduced:

1. send transaction tx1 to the target full node via RPC
2. send N more different transactions to the target full node, where N should be higher than the node's configured value for `cache_size` in `config.toml`
3. send transaction tx1 again to the target full node

One of the copies of tx1 is now _stuck_ in the mempool's data structures. Effectively causing a memory leak, and having that node gossiping that transaction to its peers forever.

The above problem can be repeated on and on until a sizable number of transactions are stuck in the mempool, in order to try to bring down the target node.

This problem is present in releases: `v0.37.0`, and `v0.37.1`, as well as in `v0.34.28`, and all previous releases of the CometBFT repo. It will be fixed in releases `v0.34.29` and `v0.37.2`.

### Patches

The PR containing the fix is [here](https://github.com/cometbft/cometbft/pull/890).


### Workarounds

* Increasing the value of `cache_size` in `config.toml` makes it very difficult to effectively attack a full node.
* Not exposing the transaction submission RPC's would mitigate the probability of a successful attack, as the attacker would then have to create a modified (byzantine) full node to be able to perform the attack via p2p.

### References

* [PR](https://github.com/tendermint/tendermint/pull/2778) that introduced the map to track transactions in the mempool.
* [PR](https://github.com/cometbft/cometbft/pull/890) containing the fix.
