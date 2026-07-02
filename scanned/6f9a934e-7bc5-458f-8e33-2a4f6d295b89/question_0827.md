# Q827: receiveFromRewardReceiver Direct ETH Donation Skew Price Update FeeReceiver P0827

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: FeeReceiver reward route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the direct ETH donation skew path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: FeeReceiver reward route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
