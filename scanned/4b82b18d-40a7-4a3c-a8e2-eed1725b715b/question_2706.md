# Q2706: getAssetDistributionData Round Down Accumulation Asset Accounting LRTOracle P2706

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the round-down accumulation path against getAssetDistributionData and look for asset accounting breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.
