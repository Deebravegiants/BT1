# Q1284: receiveFromLRTConverter Nonce Collision Attempt Converter Desync rsETH P1284

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: rsETH burn route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the nonce collision attempt path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH burn route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
