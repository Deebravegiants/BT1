# Q176: depositETH Fee Mint Limit Boundary Reentrancy queued P0176

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the fee mint limit boundary path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: queued buffer route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
