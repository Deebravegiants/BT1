# Q359: depositETH Committed Assets Desync Reentrancy Lido P0359

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the committed-assets desync path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
