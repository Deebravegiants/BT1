# [H] Miner fails to get block template when a cell used as a cell dep has been destroyed.

## Summary
Severity: High
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-07-26
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-v666-6w97-pcwm
Type: github-advisory

## Details
### Impact

The RPC `get_block_template` fails when a cell has been used as a cell dep and an input in the different transactions.

Say cell C is used as a dep group in the transaction A, and is destroyed in the transaction B.

The node adds transaction A first, then B into the transaction pool. They are both valid. But when generating the block template, if the fee rate of B is higher, it comes before A, which will invalidate A. Currently the RPC `get_block_template` will fail instead of dropping A.

### Patch

First, the `get_block_template` should not fail but dropping the conflict transactions.

Then we can propose solution to this issue. Here is an example. When a transaction is added to the pool, the pool must consider it depending on all the transactions which dep cell (direct or indirect via dep group) has been destroyed in this transaction. Because future transactions using the destroyed cells as dep will be rejected, the spending transaction only need to wait for all the existing dep transactions on chain.

### Workaround

1. Submit transaction B when A is already on chain.
2. Let B depend on A explicitly, there are several solutions:
    * a. Add any output cell on A as a dep cell or input in B.
    * b. Merge A and B. CKB allows using the same cell as both dep and input in the same transaction.
3. Ensure the fee rate of B is less than A so A always has higher priority.
