# Q1617: receiveFromNodeDelegator Rebasing Balance Drift Deposit Limit daily P1617

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the rebasing balance drift path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
