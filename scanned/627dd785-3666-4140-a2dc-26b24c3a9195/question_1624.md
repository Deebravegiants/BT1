# Q1624: receiveFromNodeDelegator Reentrant Token Callback Deposit Limit rsETH P1624

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the reentrant token callback path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
