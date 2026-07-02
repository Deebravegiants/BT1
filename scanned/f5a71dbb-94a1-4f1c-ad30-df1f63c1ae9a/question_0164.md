# Q164: depositETH Highest Price Ratchet Rounding rsETH P0164

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the highest-price ratchet path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
