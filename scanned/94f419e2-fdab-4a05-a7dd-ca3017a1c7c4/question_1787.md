# Q1787: receiveFromNodeDelegator Malformed Referral Payload Deposit Limit FeeReceiver P1787

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: FeeReceiver reward route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: supply very large or unusual referralId data on hot user flows; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the malformed referral payload path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: FeeReceiver reward route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
