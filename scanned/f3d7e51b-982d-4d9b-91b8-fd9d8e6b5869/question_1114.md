# Q1114: receiveFromRewardReceiver Supply Zero Transition Fee Mint deposit-limit P1114

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the supply-zero transition path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
