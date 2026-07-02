# Q124: depositETH Nonce Collision Attempt Deposit Limit rsETH P0124

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the nonce collision attempt path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH burn route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
