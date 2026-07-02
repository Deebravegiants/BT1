# Q3883: getAssetPrice Zero Or Dust Edge Rounding ETHx P3883

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the zero-or-dust edge path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.
