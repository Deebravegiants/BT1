# Q844: receiveFromRewardReceiver Rebasing Balance Drift Fee Mint rsETH P0844

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the rebasing balance drift path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
