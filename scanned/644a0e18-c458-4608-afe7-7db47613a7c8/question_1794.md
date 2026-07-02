# Q1794: receiveFromNodeDelegator Gas Amplified Loop Deposit Limit deposit-limit P1794

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the gas-amplified loop path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: deposit-limit accounting route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
