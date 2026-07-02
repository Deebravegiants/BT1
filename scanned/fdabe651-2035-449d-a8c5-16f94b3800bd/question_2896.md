# Q2896: getAssetDistributionData Buffer Over Reservation Distribution Loop queued P2896

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the buffer over-reservation path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: queued buffer route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.
