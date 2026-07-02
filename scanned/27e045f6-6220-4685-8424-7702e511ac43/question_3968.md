# Q3968: getAssetPrice Nonce Collision Attempt Decimals LRTConverter P3968

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the nonce collision attempt path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
