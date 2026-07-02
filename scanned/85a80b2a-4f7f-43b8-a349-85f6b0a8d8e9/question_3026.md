# Q3026: getAssetDistributionData Supply Zero Transition Distribution Loop LRTOracle P3026

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to block stuffing? Probe condition: LRTOracle price route; amount case 32 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 32 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the supply-zero transition path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTOracle price route; amount case 32 ether; timing one second after daily reset; caller model EOA caller.
