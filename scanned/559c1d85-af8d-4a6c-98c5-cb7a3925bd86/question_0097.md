# Q97: depositETH Pause Boundary Race Rounding daily P0097

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the pause boundary race path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
