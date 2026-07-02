# Q3061: getAssetDistributionData Block Timestamp Boundary Stale Balance ETH P3061

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the block-timestamp boundary path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: ETH sentinel route; amount case daily limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
