# [M] M-04 | DoS Via Frontrunning Pool Creation

## Summary
Severity: Medium
Contest weight: 0.1480
Dataset id: 1971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After the implementation of the Vault, epoch settlements and the creation of the new epoch happens at the same transaction via callbacks. Because of this atomic behavior, failure of the pool creation for the next epoch will DoS the settlement of the previous epoch. An attacker can precompute the virtual token addresses and create the Uniswap pool with these addresses as creating pools is permissionless in the Uniswap. This will cause Epoch.createValid function to revert while calling IUniswapV3Factory.createPool due to require(getPool[token0][token1][fee] == address(0)) check in the [factory.](https://github.com/Uniswap/v3-core/blob/d8b1c635c275d2a9450bd6a78f3fa2484fef73eb/contracts/UniswapV3Factory.sol#L45) The attack can cause complete blocking of the epoch settlements and creations. However, attackers must keep frontrunning and create new pools every time someone tries to settleAssertion in the optimistic oracle.

## Recommendation
Check whether the pool already exists or not by calling the getPool in the factory instead of directly calling the createPool. If the pool already exists, check whether it was already initialized or not and set the starting price. Alternatively, always make sure to use a private RPC to prevent frontrunning.
