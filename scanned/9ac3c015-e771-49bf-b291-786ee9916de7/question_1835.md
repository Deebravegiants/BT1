# Q1835: receiveFromNodeDelegator Allowance Race Deposit Limit withdrawal P1835

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the allowance race path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: withdrawal request nonce route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
