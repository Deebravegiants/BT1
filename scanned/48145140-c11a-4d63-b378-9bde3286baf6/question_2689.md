# Q2689: getAssetDistributionData Stale Price Sandwich Distribution Loop LRTUnstakingVault P2689

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the stale-price sandwich path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.
