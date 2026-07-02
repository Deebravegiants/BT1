# Q1364: receiveFromLRTConverter Buffer Over Reservation Donation Accounting rsETH P1364

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the buffer over-reservation path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
