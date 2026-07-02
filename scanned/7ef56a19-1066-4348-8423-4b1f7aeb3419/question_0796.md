# Q796: receiveFromRewardReceiver Round Up Insolvency Fee Mint queued P0796

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the round-up insolvency path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
