# Q159: depositETH Highest Price Ratchet Reentrancy Lido P0159

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the highest-price ratchet path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.
