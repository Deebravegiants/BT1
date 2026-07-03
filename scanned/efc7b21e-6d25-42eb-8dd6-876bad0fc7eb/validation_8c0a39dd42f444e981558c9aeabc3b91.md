### Title
Unexpected ETH/Token Donations to Protocol Contracts Inflate rsETH Price via Raw Balance Accounting - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getETHDistributionData()` and `getAssetDistributionData()` compute total protocol holdings using raw on-chain balances rather than internal accounting. Because `LRTDepositPool`, `NodeDelegator`, and `LRTUnstakingVault` all expose permissionless `receive()` functions, any unprivileged actor can donate ETH or supported ERC-20 tokens directly to these contracts, causing `LRTOracle._updateRsETHPrice()` to record an inflated rsETH price. Future depositors then receive fewer rsETH tokens than the protocol's stated exchange rate implies.

### Finding Description
`LRTDepositPool.getETHDistributionData()` aggregates ETH across the protocol using raw balances:

```solidity
ethLyingInDepositPool = address(this).balance;          // line 480
ethLyingInNDCs += nodeDelegatorQueue[i].balance;        // line 485
ethLyingInUnstakingVault = lrtUnstakingVault.balance;   // line 496
```

`getAssetDistributionData()` does the same for ERC-20 assets:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));          // line 444
assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);        // line 448
assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault