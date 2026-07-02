# Q1133: receiveFromRewardReceiver Unclaimed Yield Diversion Price Update Merkle-free P1133

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: Merkle-free yield accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unclaimed-yield diversion path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
