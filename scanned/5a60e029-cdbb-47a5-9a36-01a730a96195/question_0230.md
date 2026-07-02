# Q230: depositETH Failed External Call Ordering Rounding NodeDelegator P0230

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the failed external call ordering path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.
