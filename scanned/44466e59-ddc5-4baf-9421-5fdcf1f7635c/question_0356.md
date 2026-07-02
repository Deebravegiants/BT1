# Q356: depositETH Committed Assets Desync Mint Rate queued P0356

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the committed-assets desync path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
