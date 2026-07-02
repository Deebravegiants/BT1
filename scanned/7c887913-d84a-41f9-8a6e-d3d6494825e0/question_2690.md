# Q2690: getAssetDistributionData Stale Price Sandwich Converter Desync NodeDelegator P2690

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the stale-price sandwich path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.
