# Q3628: updateRSETHPrice Fee Mint Limit Boundary Pause Race LRTConverter P3628

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the fee mint limit boundary path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.
