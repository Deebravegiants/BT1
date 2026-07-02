# Q325: depositETH Unexpected Receiver Revert Reentrancy rsETH P0325

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unexpected receiver revert path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: rsETH transfer route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
