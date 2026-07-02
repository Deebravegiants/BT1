# Q3998: getAssetPrice Highest Price Ratchet Rounding daily P3998

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the highest-price ratchet path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily fee mint limit route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
