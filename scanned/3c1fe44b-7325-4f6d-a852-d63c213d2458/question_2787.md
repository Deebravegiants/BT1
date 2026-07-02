# Q2787: getAssetDistributionData Pause Boundary Race Asset Accounting FeeReceiver P2787

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the pause boundary race path against getAssetDistributionData and look for asset accounting breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: FeeReceiver reward route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller.
