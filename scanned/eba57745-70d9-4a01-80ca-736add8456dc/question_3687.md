# Q3687: updateRSETHPrice Failed External Call Ordering Fee Mint FeeReceiver P3687

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the failed external call ordering path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
