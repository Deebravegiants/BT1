# Q922: receiveFromRewardReceiver Oracle Decimal Mismatch Fee Mint stETH P0922

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: stETH supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the oracle decimal mismatch path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: stETH supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
