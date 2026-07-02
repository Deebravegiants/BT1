# Q3965: getAssetPrice Nonce Collision Attempt Rounding rsETH P3965

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the nonce collision attempt path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
