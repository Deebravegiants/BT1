# Q3688: updateRSETHPrice Failed External Call Ordering Pause Race LRTConverter P3688

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the failed external call ordering path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
