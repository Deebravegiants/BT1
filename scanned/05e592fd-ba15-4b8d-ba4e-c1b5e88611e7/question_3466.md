# Q3466: updateRSETHPrice Stale Price Sandwich Rounding LRTOracle P3466

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the stale-price sandwich path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTOracle price route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
