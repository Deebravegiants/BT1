# Q374: depositETH Block Timestamp Boundary Rounding deposit-limit P0374

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the block-timestamp boundary path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
