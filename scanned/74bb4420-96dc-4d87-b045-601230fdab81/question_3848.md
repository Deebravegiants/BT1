# Q3848: getAssetPrice Stale Price Sandwich Decimals LRTConverter P3848

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the stale-price sandwich path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing immediately after direct ETH donation; caller model EOA caller.
