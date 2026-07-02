# Q135: depositETH FirstExcludedIndex Boundary Deposit Limit withdrawal P0135

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the firstExcludedIndex boundary path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
