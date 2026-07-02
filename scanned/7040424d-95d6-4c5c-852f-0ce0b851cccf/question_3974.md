# Q3974: getAssetPrice FirstExcludedIndex Boundary Decimals deposit-limit P3974

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the firstExcludedIndex boundary path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
