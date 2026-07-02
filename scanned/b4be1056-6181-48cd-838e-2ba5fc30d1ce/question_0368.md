# Q368: depositETH Unclaimed Yield Diversion Deposit Limit LRTConverter P0368

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unclaimed-yield diversion path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
