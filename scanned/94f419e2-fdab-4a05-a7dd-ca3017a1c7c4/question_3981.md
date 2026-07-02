# Q3981: getAssetPrice FirstExcludedIndex Boundary Rounding ETH P3981

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
