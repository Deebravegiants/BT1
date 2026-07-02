# Q845: receiveFromRewardReceiver Rebasing Balance Drift Price Update rsETH P0845

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the rebasing balance drift path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
