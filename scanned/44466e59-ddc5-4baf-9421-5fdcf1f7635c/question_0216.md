# Q216: depositETH Buffer Over Reservation Pause Race queued P0216

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: queued buffer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the buffer over-reservation path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: queued buffer route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.
