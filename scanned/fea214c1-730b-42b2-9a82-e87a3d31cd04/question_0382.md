# Q382: depositETH Block Timestamp Boundary Pause Race stETH P0382

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: stETH supported asset route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the block-timestamp boundary path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: stETH supported asset route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
