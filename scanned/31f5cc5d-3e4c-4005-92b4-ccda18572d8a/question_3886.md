# Q3886: getAssetPrice Zero Or Dust Edge Decimals LRTOracle P3886

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the zero-or-dust edge path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.
