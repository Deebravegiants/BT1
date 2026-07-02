# Q354: depositETH Committed Assets Desync Pause Race deposit-limit P0354

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the committed-assets desync path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
