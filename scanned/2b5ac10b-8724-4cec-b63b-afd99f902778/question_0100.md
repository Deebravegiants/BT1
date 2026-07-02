# Q100: depositETH Pause Boundary Race Fee Mint Swell P0100

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the pause boundary race path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
