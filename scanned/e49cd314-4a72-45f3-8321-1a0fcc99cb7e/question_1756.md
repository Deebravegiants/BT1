# Q1756: receiveFromNodeDelegator Claim Replay Price Update queued P1756

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: queued buffer route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the claim replay path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: queued buffer route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
