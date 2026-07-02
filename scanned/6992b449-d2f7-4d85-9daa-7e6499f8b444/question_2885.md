# Q2885: getAssetDistributionData Buffer Under Reservation Distribution Loop rsETH P2885

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the buffer under-reservation path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.
