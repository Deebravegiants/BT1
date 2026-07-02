# Q944: receiveFromRewardReceiver Fee Mint Limit Boundary Fee Mint rsETH P0944

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: rsETH burn route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the fee mint limit boundary path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: rsETH burn route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
