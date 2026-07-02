# Q654: depositAsset Asset Identity Confusion Fee On Transfer deposit-limit P0654

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the asset identity confusion path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: deposit-limit accounting route; amount case 32.000001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
