# Q2705: getAssetDistributionData Round Down Accumulation Converter Desync rsETH P2705

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the round-down accumulation path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.
