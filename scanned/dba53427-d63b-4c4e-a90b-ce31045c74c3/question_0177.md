# Q177: depositETH Fee Mint Limit Boundary Pause Race daily P0177

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: daily mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the fee mint limit boundary path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: daily mint limit route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
