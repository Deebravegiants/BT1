# Q2790: getAssetDistributionData Pause Boundary Race Converter Desync NodeDelegator P2790

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the pause boundary race path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing exactly at daily reset; caller model EOA caller.
