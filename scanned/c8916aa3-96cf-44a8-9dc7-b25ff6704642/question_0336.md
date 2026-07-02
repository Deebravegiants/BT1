# Q336: depositETH Unexpected Receiver Revert Rounding queued P0336

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: queued buffer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the unexpected receiver revert path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: queued buffer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
