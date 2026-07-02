# Q2759: getAssetDistributionData Fee On Transfer Token Skew Stale Balance Lido P2759

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee-on-transfer token skew path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.
