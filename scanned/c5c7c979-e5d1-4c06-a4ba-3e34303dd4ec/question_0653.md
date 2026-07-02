# Q653: depositAsset Asset Identity Confusion Rounding Merkle-free P0653

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the asset identity confusion path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Merkle-free yield accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
