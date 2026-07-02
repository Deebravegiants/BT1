# Q122: depositETH Nonce Collision Attempt Fee Mint stETH P0122

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the nonce collision attempt path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: stETH supported asset route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
