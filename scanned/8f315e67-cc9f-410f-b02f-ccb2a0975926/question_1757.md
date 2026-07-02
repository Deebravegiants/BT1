# Q1757: receiveFromNodeDelegator Claim Replay Deposit Limit daily P1757

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the claim replay path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
