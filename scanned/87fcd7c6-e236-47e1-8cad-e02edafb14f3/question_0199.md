# Q199: depositETH Buffer Under Reservation Pause Race Lido P0199

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the buffer under-reservation path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Lido stETH unstake route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
