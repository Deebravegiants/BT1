# Q1115: receiveFromRewardReceiver Supply Zero Transition Price Update withdrawal P1115

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the supply-zero transition path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
