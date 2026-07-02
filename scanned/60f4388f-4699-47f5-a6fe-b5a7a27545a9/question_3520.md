# Q3520: updateRSETHPrice Fee On Transfer Token Skew Highest Price Swell P3520

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the fee-on-transfer token skew path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: Swell swETH legacy route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
