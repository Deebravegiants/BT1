# Q104: depositETH Pause Boundary Race Reentrancy rsETH P0104

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the pause boundary race path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: rsETH burn route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.
