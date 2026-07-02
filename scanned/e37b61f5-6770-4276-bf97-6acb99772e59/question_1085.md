# Q1085: receiveFromRewardReceiver Unbounded Event/data Growth Price Update rsETH P1085

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: rsETH transfer route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unbounded event/data growth path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH transfer route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
