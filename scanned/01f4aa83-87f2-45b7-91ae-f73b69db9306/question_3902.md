# Q3902: getAssetPrice Fee On Transfer Token Skew Stale Price stETH P3902

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against getAssetPrice and look for stale price breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
