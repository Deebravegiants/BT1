# Q351: depositETH Committed Assets Desync Deposit Limit EigenLayer P0351

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the committed-assets desync path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
