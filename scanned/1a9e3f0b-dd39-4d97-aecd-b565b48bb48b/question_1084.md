# Q1084: receiveFromRewardReceiver Unbounded Event/data Growth Fee Mint rsETH P1084

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: rsETH burn route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unbounded event/data growth path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: rsETH burn route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
