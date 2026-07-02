# Q1004: receiveFromRewardReceiver Failed External Call Ordering Price Update rsETH P1004

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: rsETH burn route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the failed external call ordering path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH burn route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
