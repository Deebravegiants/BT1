# Q745: depositAsset Unclaimed Yield Diversion Mint Rate rsETH P0745

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unclaimed-yield diversion path against depositAsset and look for mint rate breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: rsETH transfer route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
