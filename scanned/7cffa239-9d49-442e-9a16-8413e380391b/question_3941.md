# Q3941: getAssetPrice Pause Boundary Race Decimals ETH P3941

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the pause boundary race path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: ETH sentinel route; amount case available liquidity plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
