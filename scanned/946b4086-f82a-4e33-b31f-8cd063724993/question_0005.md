# Q5: depositETH Stale Price Sandwich Pause Race rsETH P0005

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the stale-price sandwich path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH transfer route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
