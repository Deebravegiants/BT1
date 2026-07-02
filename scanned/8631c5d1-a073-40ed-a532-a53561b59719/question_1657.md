# Q1657: receiveFromNodeDelegator Nonce Collision Attempt Deposit Limit daily P1657

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the nonce collision attempt path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
