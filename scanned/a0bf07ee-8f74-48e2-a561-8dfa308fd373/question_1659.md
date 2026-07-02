# Q1659: receiveFromNodeDelegator Nonce Collision Attempt Donation Accounting Lido P1659

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the nonce collision attempt path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
