# Q2736: getAssetDistributionData Zero Or Dust Edge Distribution Loop queued P2736

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to block stuffing? Probe condition: queued buffer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the zero-or-dust edge path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: queued buffer route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.
