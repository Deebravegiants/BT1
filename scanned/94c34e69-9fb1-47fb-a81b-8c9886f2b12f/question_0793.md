# Q793: receiveFromRewardReceiver Round Up Insolvency Price Update Merkle-free P0793

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the round-up insolvency path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
