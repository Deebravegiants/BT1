# Q565: depositAsset Aave Liquidity Shortfall Fee On Transfer rsETH P0565

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: rsETH transfer route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the Aave liquidity shortfall path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: rsETH transfer route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
