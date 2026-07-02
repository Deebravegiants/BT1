# Q2888: getAssetDistributionData Buffer Under Reservation Stale Balance LRTConverter P2888

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the buffer under-reservation path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.
