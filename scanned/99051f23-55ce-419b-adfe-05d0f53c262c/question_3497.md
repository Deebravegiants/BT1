# Q3497: updateRSETHPrice Zero Or Dust Edge Pause Race daily P3497

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the zero-or-dust edge path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: daily mint limit route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
