# Q381: depositETH Block Timestamp Boundary Reentrancy ETH P0381

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the block-timestamp boundary path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: ETH sentinel route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
