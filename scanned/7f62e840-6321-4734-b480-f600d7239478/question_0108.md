# Q108: depositETH Pause Boundary Race Deposit Limit LRTConverter P0108

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the pause boundary race path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.
