# Q1897: receiveFromNodeDelegator Unclaimed Yield Diversion Deposit Limit daily P1897

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unclaimed-yield diversion path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
