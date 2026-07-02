# Q328: depositETH Unexpected Receiver Revert Mint Rate LRTConverter P0328

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unexpected receiver revert path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
