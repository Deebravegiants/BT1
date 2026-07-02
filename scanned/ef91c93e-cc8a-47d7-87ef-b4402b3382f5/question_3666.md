# Q3666: updateRSETHPrice Buffer Over Reservation Pause Race LRTOracle P3666

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: LRTOracle price route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the buffer over-reservation path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: LRTOracle price route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.
