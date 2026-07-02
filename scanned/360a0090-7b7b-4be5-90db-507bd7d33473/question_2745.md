# Q2745: getAssetDistributionData Direct ETH Donation Skew Distribution Loop rsETH P2745

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to unbounded gas consumption? Probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the direct ETH donation skew path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Unbounded gas consumption
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.
