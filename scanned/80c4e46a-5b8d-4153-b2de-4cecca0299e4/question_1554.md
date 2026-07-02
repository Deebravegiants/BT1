# Q1554: receiveFromNodeDelegator Round Down Accumulation Deposit Limit deposit-limit P1554

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the round-down accumulation path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
