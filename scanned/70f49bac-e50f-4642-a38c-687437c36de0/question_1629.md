# Q1629: receiveFromNodeDelegator Reentrant Token Callback Withdrawal Liquidity LRTUnstakingVault P1629

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the reentrant token callback path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
