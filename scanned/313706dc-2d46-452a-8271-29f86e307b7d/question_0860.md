# Q860: receiveFromRewardReceiver Reentrant Token Callback Price Update Swell P0860

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the reentrant token callback path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
