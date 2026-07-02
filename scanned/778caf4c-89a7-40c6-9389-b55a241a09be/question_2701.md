# Q2701: getAssetDistributionData Round Down Accumulation Converter Desync ETH P2701

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the round-down accumulation path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.
