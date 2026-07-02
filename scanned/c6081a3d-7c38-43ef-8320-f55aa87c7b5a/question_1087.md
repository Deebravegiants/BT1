# Q1087: receiveFromRewardReceiver Unbounded Event/data Growth Donation Accounting FeeReceiver P1087

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the unbounded event/data growth path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: FeeReceiver reward route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
