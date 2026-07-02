# Q3484: updateRSETHPrice Round Up Insolvency Price Update rsETH P3484

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the round-up insolvency path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
