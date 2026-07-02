# Q2828: getAssetDistributionData FirstExcludedIndex Boundary Asset Accounting LRTConverter P2828

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the firstExcludedIndex boundary path against getAssetDistributionData and look for asset accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.
