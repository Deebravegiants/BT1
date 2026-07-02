# Q200: depositETH Buffer Under Reservation Fee Mint Swell P0200

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the buffer under-reservation path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Swell swETH legacy route; amount case 1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
