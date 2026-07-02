# Q1002: receiveFromRewardReceiver Failed External Call Ordering Donation Accounting stETH P1002

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the failed external call ordering path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: stETH supported asset route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
