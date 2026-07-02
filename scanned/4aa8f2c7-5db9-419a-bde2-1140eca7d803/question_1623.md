# Q1623: receiveFromNodeDelegator Reentrant Token Callback Price Update ETHx P1623

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the reentrant token callback path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETHx supported asset route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
