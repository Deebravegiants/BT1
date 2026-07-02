# Q762: depositAsset Block Timestamp Boundary Mint Rate stETH P0762

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the block-timestamp boundary path against depositAsset and look for mint rate breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: stETH supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
