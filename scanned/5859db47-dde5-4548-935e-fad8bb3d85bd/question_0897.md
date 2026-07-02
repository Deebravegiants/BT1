# Q897: receiveFromRewardReceiver Nonce Collision Attempt Price Update daily P0897

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the nonce collision attempt path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
