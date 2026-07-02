# Q2725: getAssetDistributionData Zero Or Dust Edge Stale Balance rsETH P2725

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: rsETH transfer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the zero-or-dust edge path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: rsETH transfer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.
