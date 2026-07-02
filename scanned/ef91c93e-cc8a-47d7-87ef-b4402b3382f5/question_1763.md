# Q1763: receiveFromNodeDelegator Claim Replay Donation Accounting ETHx P1763

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the claim replay path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: ETHx supported asset route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
