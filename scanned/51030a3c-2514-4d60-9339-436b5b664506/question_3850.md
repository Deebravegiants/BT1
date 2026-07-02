# Q3850: getAssetPrice Stale Price Sandwich Rounding NodeDelegator P3850

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the stale-price sandwich path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.
