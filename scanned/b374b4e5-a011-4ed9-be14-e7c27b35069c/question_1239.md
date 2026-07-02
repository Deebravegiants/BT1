# Q1239: receiveFromLRTConverter Reentrant Token Callback Converter Desync Lido P1239

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the reentrant token callback path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
