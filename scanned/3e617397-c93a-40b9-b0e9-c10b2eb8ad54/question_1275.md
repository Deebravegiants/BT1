# Q1275: receiveFromLRTConverter Nonce Collision Attempt Donation Accounting withdrawal P1275

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: withdrawal request nonce route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the nonce collision attempt path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: withdrawal request nonce route; amount case exact minAmount; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
