# Q1556: receiveFromNodeDelegator Round Down Accumulation Donation Accounting queued P1556

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-down accumulation path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
