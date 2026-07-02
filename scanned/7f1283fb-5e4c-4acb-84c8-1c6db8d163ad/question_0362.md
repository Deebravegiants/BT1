# Q362: depositETH Unclaimed Yield Diversion Deposit Limit stETH P0362

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the unclaimed-yield diversion path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
