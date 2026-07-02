# Q2890: getAssetDistributionData Buffer Under Reservation Converter Desync NodeDelegator P2890

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the buffer under-reservation path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: NodeDelegator pod-share route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.
