# Q3525: updateRSETHPrice Fee On Transfer Token Skew Highest Price rsETH P3525

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the fee-on-transfer token skew path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: rsETH transfer route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.
