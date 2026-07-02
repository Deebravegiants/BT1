# Q282: depositETH Min Amount Bypass Pause Race stETH P0282

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the min-amount bypass path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: stETH supported asset route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.
