# Q3460: updateRSETHPrice Stale Price Sandwich Highest Price Swell P3460

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the stale-price sandwich path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.
