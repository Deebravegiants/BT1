# Q668: depositAsset Min Amount Bypass Mint Rate LRTConverter P0668

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the min-amount bypass path against depositAsset and look for mint rate breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
