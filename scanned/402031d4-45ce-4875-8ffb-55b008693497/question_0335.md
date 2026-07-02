# Q335: depositETH Unexpected Receiver Revert Deposit Limit withdrawal P0335

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unexpected receiver revert path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: withdrawal request nonce route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
