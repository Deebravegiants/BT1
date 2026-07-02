# Q121: depositETH Nonce Collision Attempt Pause Race ETH P0121

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: ETH sentinel route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the nonce collision attempt path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: ETH sentinel route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
