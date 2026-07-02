# Q3486: updateRSETHPrice Round Up Insolvency Pause Race LRTOracle P3486

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the round-up insolvency path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: LRTOracle price route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
