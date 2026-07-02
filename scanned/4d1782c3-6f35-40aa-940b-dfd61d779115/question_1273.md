# Q1273: receiveFromLRTConverter Nonce Collision Attempt Price Update Merkle-free P1273

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use single transaction to exercise the nonce collision attempt path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
