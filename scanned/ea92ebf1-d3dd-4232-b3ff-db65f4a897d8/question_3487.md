# Q3487: updateRSETHPrice Round Up Insolvency Highest Price FeeReceiver P3487

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-up insolvency path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: FeeReceiver reward route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
