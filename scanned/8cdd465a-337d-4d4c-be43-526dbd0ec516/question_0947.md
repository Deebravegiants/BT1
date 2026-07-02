# Q947: receiveFromRewardReceiver Fee Mint Limit Boundary Donation Accounting FeeReceiver P0947

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee mint limit boundary path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
