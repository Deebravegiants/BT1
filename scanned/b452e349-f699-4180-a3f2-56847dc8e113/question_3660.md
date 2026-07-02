# Q3660: updateRSETHPrice Buffer Under Reservation Pause Race Swell P3660

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the buffer under-reservation path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
