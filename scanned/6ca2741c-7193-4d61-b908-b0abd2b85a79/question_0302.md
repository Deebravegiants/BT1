# Q302: depositETH Cross Contract Stale Read Rounding stETH P0302

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the cross-contract stale read path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
