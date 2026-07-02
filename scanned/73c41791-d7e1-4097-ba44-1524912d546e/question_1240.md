# Q1240: receiveFromLRTConverter Reentrant Token Callback Price Update Swell P1240

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the reentrant token callback path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Swell swETH legacy route; amount case 2 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
