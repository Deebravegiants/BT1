# Q1373: receiveFromLRTConverter Claim Replay Price Update Merkle-free P1373

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the claim replay path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
