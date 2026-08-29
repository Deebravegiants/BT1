# [M] Unhandled reverts from Cosmos to Eth batches can cause *Denial Of Service*

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/56
Type: code-finding

## Details
# Handle

hack3r-0m


# Vulnerability details

https://github.com/althea-net/cosmos-gravity-bridge/blob/main/solidity/contracts/Gravity.sol#L400

At the above-mentioned places in Gravity contract, it makes external call to a function to transfer erc20 token. This can cause revert in cases where erc20 safeTransfer fails (for e.g erc20 contract has blacklisted address of gravity contract to alllow transfers) and hence,`TransactionBatchExecutedEvent` event will not be emitted resulting in pending state and not updating nonces.

https://github.com/althea-net/cosmos-gravity-bridge/blob/92d0e12cea813305e6472851beeb80bd2eaf858d/orchestrator/relayer/src/batch_relaying.rs#L229-L244

At relayer level, gas estimation will fail and result in panic while unwrapping. If such transfer transactions puts high fee to get picked up by relayer then especially causing more damage.

Introduce a mechanism to filter such scenarios so they are not picked by relayers frequently
